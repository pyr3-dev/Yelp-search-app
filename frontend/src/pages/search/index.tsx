import { useEffect, useState } from "react";
import { useSearchStore } from "@/store/search-store";
import {
  fetchBusinesses,
  fetchBusinessDetail,
  fetchBusinessPhotos,
} from "@/services/businesses";
import { ResultList } from "./result-list";
import { DetailPanel } from "@/components/detail-panel";
import { EmptyState } from "@/components/empty-state";
import type { BusinessDetail, BusinessResult, PhotoResult } from "@/types";

const LIMIT = 20;

export function SearchPage() {
  const { city, name, scope, category, minStars, sortBy, order, page, selectedId } =
    useSearchStore();

  // List state
  const [results, setResults] = useState<BusinessResult[]>([]);
  const [total, setTotal] = useState(0);
  const [listLoading, setListLoading] = useState(false);
  const [listError, setListError] = useState<string | null>(null);

  // Detail state
  const [detail, setDetail] = useState<BusinessDetail | null>(null);
  const [photos, setPhotos] = useState<PhotoResult[]>([]);
  const [detailLoading, setDetailLoading] = useState(false);
  const [detailError, setDetailError] = useState<string | null>(null);

  // Fetch list when search params change
  useEffect(() => {
    if (!city) return;
    setResults([]);
    setListLoading(true);
    setListError(null);
    fetchBusinesses({
      city,
      ...(name ? { name } : {}),
      ...(scope ? { scope } : {}),
      ...(category ? { category } : {}),
      ...(minStars != null ? { min_stars: minStars } : {}),
      sort_by: sortBy,
      order,
      page,
      limit: LIMIT,
    })
      .then((data) => {
        setResults(data.results);
        setTotal(data.total);
      })
      .catch(() =>
        setListError("Failed to load results. Is the backend running?"),
      )
      .finally(() => setListLoading(false));
  }, [city, name, scope, category, minStars, sortBy, order, page]);

  // Fetch detail + photos when selected business changes
  useEffect(() => {
    if (!selectedId) {
      setDetail(null);
      setPhotos([]);
      return;
    }
    setDetailLoading(true);
    setDetailError(null);
    Promise.all([
      fetchBusinessDetail(selectedId),
      fetchBusinessPhotos(selectedId),
    ])
      .then(([d, p]) => {
        setDetail(d);
        setPhotos(p);
      })
      .catch(() => {
        setDetail(null);
        setPhotos([]);
        setDetailError("Failed to load business details.");
      })
      .finally(() => setDetailLoading(false));
  }, [selectedId]);

  const showEmptyList = !city || (!listLoading && results.length === 0);

  return (
    <div className="flex h-full overflow-hidden">
      {/* Left panel */}
      <div className="w-80 border-r border-slate-200 flex flex-col shrink-0 bg-white">
        {showEmptyList && !listLoading ? (
          <EmptyState variant={city ? "no-results" : "idle"} />
        ) : listError ? (
          <div className="p-4 text-xs text-red-500">{listError}</div>
        ) : (
          <ResultList
            results={results}
            total={total}
            limit={LIMIT}
            loading={listLoading}
          />
        )}
      </div>

      {/* Right panel */}
      <div className="flex-1 bg-slate-50 overflow-hidden">
        {detailError ? (
          <div className="flex items-center justify-center h-full text-xs text-red-500">
            {detailError}
          </div>
        ) : (
          <DetailPanel
            business={detail}
            photos={photos}
            loading={detailLoading}
          />
        )}
      </div>
    </div>
  );
}
