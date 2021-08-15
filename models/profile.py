from sqlalchemy import Column
from sqlalchemy.dialects.postgresql import UUID
import datetime
import secrets

from common.extensions import db


def _generate_shared_secret():
    return secrets.token_urlsafe(16)


class Profile(db.Model):
    __tablename__ = "profile"
    id = Column(db.Integer,
                primary_key=True)
    created_on = db.Column(
        "created_on",
        db.DateTime(timezone=True),
        default=datetime.datetime.utcnow,
        server_default=db.func.now(),
        nullable=False,
    )
    timestamp_uninstall = db.Column(db.DateTime(timezone=True),
                                    nullable=True)
    timestamp_blacklisted = db.Column(db.DateTime(timezone=True),
                                      nullable=True)
    name = db.Column(db.String(128),
                     nullable=True)
    contact_email = db.Column(db.String(128),
                              nullable=True)
    customer_id = db.Column(UUID(as_uuid=True),
                            nullable=True)
    # status of profile, currently not used anywhere but maybe one day? ;)
    status = Column(db.SmallInteger, default=1)
    # Used to validate api requests from for example Shopify
    auth_token = Column(db.String(256),
                        default=_generate_shared_secret)

    shop_unique_id = Column(db.String(256))  # For shopify this is the same as the shop url
    shop_url = Column(db.String(256))
    # The Shopify access token
    shopify_access_token = Column(db.String(256),
                                  nullable=True)
    shopify_recurring_subscription_id = db.Column(db.String(256),
                                                  nullable=True)
    onboarding_shopify_added_webhooks = db.Column(db.Boolean,
                                                           default=False)

    @staticmethod
    def check_token(token):
        profile = Profile.query.filter_by(auth_token=token).first()
        if profile is None:
            return None
        return profile
