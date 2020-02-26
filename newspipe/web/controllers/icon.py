import base64
import requests
from web.models import Icon
from .abstract import AbstractController


class IconController(AbstractController):
    _db_cls = Icon
    _user_id_key = None

    def _build_from_url(self, attrs):
        if "url" in attrs and "content" not in attrs:
            resp = requests.get(attrs["url"], verify=False)
            attrs.update(
                {
                    "url": resp.url,
                    "mimetype": resp.headers.get("content-type", None),
                    "content": base64.b64encode(resp.content).decode("utf8"),
                }
            )
        return attrs

    def create(self, **attrs):
        return super().create(**self._build_from_url(attrs))

    def update(self, filters, attrs):
        return super().update(filters, self._build_from_url(attrs))
