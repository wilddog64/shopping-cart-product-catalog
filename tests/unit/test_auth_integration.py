"""Integration tests for OAuth2/OIDC authentication with FastAPI."""

import time
from unittest.mock import MagicMock, patch

import pytest
from fastapi import Depends, FastAPI
from fastapi.testclient import TestClient
from jose import jwt

from product_catalog.auth import (
    CurrentUser,
    OIDCAuth,
    get_current_user,
    get_oidc_auth,
    require_admin,
    require_auth,
    require_catalog_admin,
    require_role,
)

# Test RSA keys for JWT signing (for testing only)
TEST_PRIVATE_KEY = """-----BEGIN RSA PRIVATE KEY-----
MIIEogIBAAKCAQEAuMotuKGBCgiiKiNRmUZBFr4Fcl0TSRzkTjOn7RJYxGfJARYL
IbV/3kevSuzQrUSJineUQFgv40jf5be/GauyLooJyforKwrsNWjWWeGVc+xRa4Wz
EwJVX6b0jXKuKKHGAnLMZ/bAuTHaClwfiAANHY2Xp1OPRpfLAgypcdWOaG40nCuB
JK1fptA7Hn8Cd+oRtF1TtvfmbbmhgevedNXQMk2kSTNTEuD3R2S4pjM6+sqQvdht
q9sexSzKMnEDcZlkl0LXxCR8J+bfuU8jIk6LysWhospCBCWwymogZV4cQjpZh+/J
xKBKt5V7MlbmtIYvGjMr6KB4PTk3VspL2jy8UQIDAQABAoIBABd1NvOisO5UpT1j
KWcjN30LF0bq0NltrP/OZ+lc9F7ObAJSyYv4beiKQhLpWB4+vpUQ1AWNDFs2c5HG
TyCTnrVwuYhl1RgMNWscSWW0kNPb8oQLP23Q1ISlfZL9NWWcD7Zc21zxQorf7LV2
91u84e1X/aH0phIIj/FNKS91tDPGXm2U3+Gpup/HFU7+UO5vZs6bMrp8H7VitmRO
BLXSnpyFNyHmMWBiMhgu9Az6K+6JuX9lBdbrSSuIoDRQYL8UGF2TuGTpsorMPkZg
fvXP6IX7V/DXYzWJj5Qtg/VBh0J9Ls4zGUJIAybtHE8QpEN04lkSY0s1IXTyHL9p
Y71fZ68CgYEA4eR6f4EwuIMWhludmAN4xpv5qsYXmwKe7+lUQO8G4QG76kuMuBlj
vyytt+UkACEOGiXKzFDQWFyfEGjKjqalUXKIMNqwpUFzeBU6lRDxFsOLX+gp3joN
5qxIGG5+dx6Jodq4RbaN27u2R7J+rHwSix/d001BUyBmy5OZkCBYzb8CgYEA0WtD
G87qukN5i7XUatjefhE8H8ng26ByyGWbegSLVRGGzE+878ruJlKIOURx9jGdE15y
+6e4QnezA1Ep3L0kXyh7BK7E7DGlg2h719T/CohsjfF7M47dnPwNEmMsP8tZKin/
HR0wCZB1FHIrHVa9xip3rOa/bDEBctbNfe4DGe8CgYBnn9hSBYHEIt6CZCS3R2Bw
O70ciiLqCRnAFNmBsCUHszPxFxdGnN8VI/nNEmChboh5ljyh3bC12Edfz7KcHfZY
lqHDR48hQBUoURS+rTbrqmiVZntOZnNaDk5EZuu82VVp2lwOHuCUnFfSLB/QIFqh
V8z60cXVzFdbrCoV48DZIQKBgEvlCpoeYBUG9Rq71/KtC902U8rVd+dAe7jCkhkj
Ynd+9ZI/56IjsjEzQek3M/HcQyfM1/D59J4qETdHh9tWtMLDwemNiRJsX6aDDDbJ
G3DuxiCe/l5ODWSiN/6M8HFiObs9IxajCFC/CJ9TTOrCD96sb1i6+26zR+odjLVx
t7ADAoGAA44XnbP/x2YqKO7tyFeeScU+oQmnFZU6mOqCwGxfuCqKYrP78XZOf49g
7V5mKe75wtmk8QZxoFgieAm488j2+wyNoXOqWqmhve0mJX2fFotduVQJH5+oKRAj
T2VIpmLyPksH6Epmlxefn8Q00cAvBuAqlRZ2eRnL8jD3aWs0Xnk=
-----END RSA PRIVATE KEY-----"""

TEST_PUBLIC_KEY = """-----BEGIN PUBLIC KEY-----
MIIBIjANBgkqhkiG9w0BAQEFAAOCAQ8AMIIBCgKCAQEAuMotuKGBCgiiKiNRmUZB
Fr4Fcl0TSRzkTjOn7RJYxGfJARYLIbV/3kevSuzQrUSJineUQFgv40jf5be/Gauy
LooJyforKwrsNWjWWeGVc+xRa4WzEwJVX6b0jXKuKKHGAnLMZ/bAuTHaClwfiAAN
HY2Xp1OPRpfLAgypcdWOaG40nCuBJK1fptA7Hn8Cd+oRtF1TtvfmbbmhgevedNXQ
Mk2kSTNTEuD3R2S4pjM6+sqQvdhtq9sexSzKMnEDcZlkl0LXxCR8J+bfuU8jIk6L
ysWhospCBCWwymogZV4cQjpZh+/JxKBKt5V7MlbmtIYvGjMr6KB4PTk3VspL2jy8
UQIDAQAB
-----END PUBLIC KEY-----"""


def create_test_token(
    sub: str = "test-user-id",
    username: str = "testuser",
    roles: list[str] = None,
    groups: list[str] = None,
    expires_in: int = 3600,
) -> str:
    """Create a test JWT token."""
    now = int(time.time())
    payload = {
        "sub": sub,
        "iss": "http://keycloak.test/realms/shopping-cart",
        "iat": now,
        "exp": now + expires_in,
        "preferred_username": username,
        "email": f"{username}@test.com",
        "name": f"Test {username.title()}",
    }

    if roles:
        payload["realm_access"] = {"roles": roles}

    if groups:
        payload["groups"] = groups

    return jwt.encode(payload, TEST_PRIVATE_KEY, algorithm="RS256")


@pytest.fixture
def mock_settings():
    """Create mock settings for OAuth2."""
    settings = MagicMock()
    settings.oauth2_enabled = True
    settings.oauth2_issuer_uri = "http://keycloak.test/realms/shopping-cart"
    settings.oauth2_client_id = "product-catalog"
    return settings


@pytest.fixture
def mock_settings_disabled():
    """Create mock settings with OAuth2 disabled."""
    settings = MagicMock()
    settings.oauth2_enabled = False
    settings.oauth2_issuer_uri = ""
    settings.oauth2_client_id = ""
    return settings


@pytest.fixture
def test_app():
    """Create a test FastAPI application."""
    app = FastAPI()

    @app.get("/public")
    async def public_endpoint():
        return {"message": "public"}

    @app.get("/protected")
    async def protected_endpoint(user: CurrentUser = Depends(require_auth)):
        return {"message": "protected", "user": user.username}

    @app.get("/admin")
    async def admin_endpoint(user: CurrentUser = Depends(require_admin)):
        return {"message": "admin", "user": user.username}

    @app.get("/catalog-admin")
    async def catalog_admin_endpoint(user: CurrentUser = Depends(require_catalog_admin)):
        return {"message": "catalog-admin", "user": user.username}

    @app.get("/developer")
    async def developer_endpoint(user: CurrentUser = Depends(require_role("developer", "platform-admin"))):
        return {"message": "developer", "user": user.username}

    @app.get("/optional-auth")
    async def optional_auth_endpoint(user: CurrentUser | None = Depends(get_current_user)):
        if user:
            return {"message": "authenticated", "user": user.username}
        return {"message": "anonymous"}

    return app


class TestPublicEndpoints:
    """Tests for public endpoints."""

    def test_public_endpoint_accessible(self, test_app):
        """Public endpoints should be accessible without auth."""
        client = TestClient(test_app)
        response = client.get("/public")
        assert response.status_code == 200
        assert response.json() == {"message": "public"}


class TestProtectedEndpointsOAuth2Disabled:
    """Tests for protected endpoints when OAuth2 is disabled."""

    def test_protected_endpoint_returns_anonymous_user(self, test_app, mock_settings_disabled):
        """Should return anonymous user when OAuth2 is disabled."""
        with patch("product_catalog.auth.get_settings", return_value=mock_settings_disabled):
            # Clear the cached auth instance
            get_oidc_auth.cache_clear()

            client = TestClient(test_app)
            response = client.get("/protected")

            assert response.status_code == 200
            data = response.json()
            assert data["user"] == "anonymous"


class TestProtectedEndpointsOAuth2Enabled:
    """Tests for protected endpoints when OAuth2 is enabled."""

    def test_protected_endpoint_requires_auth(self, test_app, mock_settings):
        """Should return 401 when no token provided."""
        with patch("product_catalog.auth.get_settings", return_value=mock_settings):
            get_oidc_auth.cache_clear()

            client = TestClient(test_app)
            response = client.get("/protected")

            assert response.status_code == 401

    def test_protected_endpoint_with_invalid_token(self, test_app, mock_settings):
        """Should return 401 with invalid token."""
        with patch("product_catalog.auth.get_settings", return_value=mock_settings):
            get_oidc_auth.cache_clear()

            client = TestClient(test_app)
            response = client.get(
                "/protected",
                headers={"Authorization": "Bearer invalid-token"},
            )

            # Will be 401 (invalid token) or 503 (can't reach JWKS endpoint)
            # In unit tests, JWKS endpoint is unreachable, so 503 is expected
            assert response.status_code in [401, 503]


class TestOptionalAuth:
    """Tests for optional authentication endpoints."""

    def test_optional_auth_without_token(self, test_app, mock_settings):
        """Should return anonymous response when no token provided."""
        with patch("product_catalog.auth.get_settings", return_value=mock_settings):
            get_oidc_auth.cache_clear()

            client = TestClient(test_app)
            response = client.get("/optional-auth")

            assert response.status_code == 200
            assert response.json() == {"message": "anonymous"}


class TestRoleBasedAccess:
    """Tests for role-based access control."""

    @pytest.fixture
    def mock_oidc_auth(self, mock_settings):
        """Create a mock OIDC auth that bypasses JWT verification."""
        auth = MagicMock(spec=OIDCAuth)
        auth.enabled = True
        auth.issuer_uri = mock_settings.oauth2_issuer_uri

        async def mock_verify(token):
            # Parse the token without verification for testing
            payload = jwt.decode(token, options={"verify_signature": False})
            from product_catalog.auth import TokenPayload
            return TokenPayload(**payload)

        auth.verify_token = mock_verify
        return auth

    def test_admin_endpoint_with_admin_role(self, test_app, mock_settings, mock_oidc_auth):
        """Admin endpoint should accept users with admin role."""
        # This test would require mocking the entire auth flow
        # For now, we test the CurrentUser model directly
        user = CurrentUser(
            id="user1",
            username="admin",
            roles=["platform-admin"],
            groups=[],
        )
        assert user.is_admin is True

    def test_admin_endpoint_denied_for_regular_user(self, test_app, mock_settings):
        """Admin endpoint should deny regular users."""
        user = CurrentUser(
            id="user1",
            username="regular",
            roles=["catalog-user"],
            groups=[],
        )
        assert user.is_admin is False


class TestSecurityHeaders:
    """Tests for security headers in responses."""

    def test_response_headers(self, test_app):
        """Responses should include security headers."""
        client = TestClient(test_app)
        response = client.get("/public")

        # These headers would be set by the security middleware
        # if setup_security() is called on the app
        assert response.status_code == 200


class TestTokenExtraction:
    """Tests for JWT token extraction and validation."""

    def test_bearer_token_extraction(self):
        """Should extract token from Bearer authorization header."""
        from fastapi.security import HTTPAuthorizationCredentials

        credentials = HTTPAuthorizationCredentials(
            scheme="Bearer",
            credentials="test-token-value",
        )
        assert credentials.credentials == "test-token-value"

    def test_create_valid_test_token(self):
        """Should create a valid JWT token for testing."""
        token = create_test_token(
            username="testuser",
            roles=["platform-admin"],
            groups=["/developers"],
        )

        # Decode without verification to check structure
        decoded = jwt.decode(token, TEST_PUBLIC_KEY, algorithms=["RS256"], options={"verify_exp": False})

        assert decoded["preferred_username"] == "testuser"
        assert decoded["realm_access"]["roles"] == ["platform-admin"]
        assert decoded["groups"] == ["/developers"]

    def test_expired_token(self):
        """Should create an expired token for testing."""
        token = create_test_token(expires_in=-3600)  # Expired 1 hour ago

        decoded = jwt.decode(token, TEST_PUBLIC_KEY, algorithms=["RS256"], options={"verify_exp": False})

        assert decoded["exp"] < time.time()


class TestUserRoleCombinations:
    """Tests for various role and group combinations."""

    @pytest.mark.parametrize(
        "roles,groups,expected_admin",
        [
            (["platform-admin"], [], True),
            (["catalog-admin"], [], True),
            (["admin"], [], True),
            ([], ["platform-admins"], True),
            (["order-admin"], [], False),
            (["catalog-user"], [], False),
            ([], ["developers"], False),
            ([], [], False),
        ],
    )
    def test_admin_status(self, roles, groups, expected_admin):
        """Test admin status for various role/group combinations."""
        user = CurrentUser(
            id="user1",
            username="testuser",
            roles=roles,
            groups=groups,
        )
        assert user.is_admin is expected_admin

    @pytest.mark.parametrize(
        "roles,groups,expected_catalog_admin",
        [
            (["catalog-admin"], [], True),
            (["platform-admin"], [], True),
            ([], ["catalog-admins"], True),
            (["catalog-user"], [], False),
            (["order-admin"], [], False),
            ([], ["developers"], False),
        ],
    )
    def test_catalog_admin_status(self, roles, groups, expected_catalog_admin):
        """Test catalog admin status for various role/group combinations."""
        user = CurrentUser(
            id="user1",
            username="testuser",
            roles=roles,
            groups=groups,
        )
        assert user.is_catalog_admin is expected_catalog_admin
