def test_models_have_correct_tablenames():
    from models import Business, YelpUser, Review, Tip, Checkin, Photo

    assert Business.__tablename__ == "business"
    assert YelpUser.__tablename__ == "yelp_user"
    assert Review.__tablename__ == "review"
    assert Tip.__tablename__ == "tip"
    assert Checkin.__tablename__ == "checkin"
    assert Photo.__tablename__ == "photo"
