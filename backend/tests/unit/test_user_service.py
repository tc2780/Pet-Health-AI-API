"""
Comprehensive unit tests for UserService
"""
import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from typing import Optional

from app.services.user import UserService
from app.models.user import User
from app.schemas.user import UserCreate, UserUpdate


class TestUserServiceQueries:
    """Unit tests for user query operations"""
    
    @pytest.fixture
    def user_service(self):
        """UserService with mocked database"""
        mock_session = AsyncMock()
        return UserService(mock_session)
    
    @pytest.fixture
    def sample_user(self):
        """Sample user for testing"""
        return User(
            id="user-123",
            email="test@example.com",
            username="testuser",
            password_hash="hashed_password",
            is_active=True
        )
    
    async def test_get_user_by_id_found(self, user_service, sample_user):
        """Test getting user by ID when user exists"""
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = sample_user
        user_service.db.execute = AsyncMock(return_value=mock_result)
        
        result = await user_service.get_user_by_id("user-123")
        
        assert result == sample_user
        user_service.db.execute.assert_called_once()
    
    async def test_get_user_by_id_not_found(self, user_service):
        """Test getting user by ID when user doesn't exist"""
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = None
        user_service.db.execute = AsyncMock(return_value=mock_result)
        
        result = await user_service.get_user_by_id("nonexistent-id")
        
        assert result is None
    
    async def test_get_user_by_email_found(self, user_service, sample_user):
        """Test getting user by email when user exists"""
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = sample_user
        user_service.db.execute = AsyncMock(return_value=mock_result)
        
        result = await user_service.get_user_by_email("test@example.com")
        
        assert result == sample_user
    
    async def test_get_user_by_email_not_found(self, user_service):
        """Test getting user by email when user doesn't exist"""
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = None
        user_service.db.execute = AsyncMock(return_value=mock_result)
        
        result = await user_service.get_user_by_email("nonexistent@example.com")
        
        assert result is None
    
    async def test_get_user_by_username_found(self, user_service, sample_user):
        """Test getting user by username when user exists"""
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = sample_user
        user_service.db.execute = AsyncMock(return_value=mock_result)
        
        result = await user_service.get_user_by_username("testuser")
        
        assert result == sample_user
    
    async def test_get_user_by_username_not_found(self, user_service):
        """Test getting user by username when user doesn't exist"""
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = None
        user_service.db.execute = AsyncMock(return_value=mock_result)
        
        result = await user_service.get_user_by_username("nonexistent")
        
        assert result is None


class TestUserServiceCreate:
    """Unit tests for user creation operations"""
    
    @pytest.fixture
    def user_service(self):
        mock_session = AsyncMock()
        return UserService(mock_session)
    
    @pytest.fixture
    def user_create_data(self):
        """Sample user creation data"""
        return UserCreate(
            email="newuser@example.com",
            username="newuser",
            password="secure_password123"
        )
    
    async def test_create_user_success(self, user_service, user_create_data):
        """Test successful user creation"""
        mock_user = User(
            id="user-456",
            email="newuser@example.com",
            username="newuser",
            password_hash="hashed_secure_password123"
        )
        
        user_service.db.add = MagicMock()
        user_service.db.commit = AsyncMock()
        user_service.db.refresh = AsyncMock()
        
        with patch('app.services.user.get_password_hash') as mock_hash:
            mock_hash.return_value = "hashed_secure_password123"
            
            with patch('app.services.user.User', return_value=mock_user):
                result = await user_service.create_user(user_create_data)
            
            mock_hash.assert_called_once_with("secure_password123")
            user_service.db.add.assert_called_once()
            user_service.db.commit.assert_called_once()
            user_service.db.refresh.assert_called_once()
            
            assert result == mock_user
    
    async def test_create_user_password_hashing(self, user_service, user_create_data):
        """Test that password is properly hashed during user creation"""
        with patch('app.services.user.get_password_hash') as mock_hash:
            mock_hash.return_value = "super_secure_hash"
            
            with patch('app.services.user.User') as mock_user_model:
                user_service.db.add = MagicMock()
                user_service.db.commit = AsyncMock()
                user_service.db.refresh = AsyncMock()
                
                await user_service.create_user(user_create_data)
                
                mock_hash.assert_called_once_with("secure_password123")
                # Verify User model was called with hashed password
                mock_user_model.assert_called_once()
                call_kwargs = mock_user_model.call_args[1]
                assert call_kwargs['password_hash'] == "super_secure_hash"
    
    async def test_create_user_sets_default_flags(self, user_service, user_create_data):
        """Test that new user has correct default flags"""
        with patch('app.services.user.get_password_hash', return_value="hashed"):
            with patch('app.services.user.User') as mock_user_model:
                user_service.db.add = MagicMock()
                user_service.db.commit = AsyncMock()
                user_service.db.refresh = AsyncMock()
                
                await user_service.create_user(user_create_data)
                
                mock_user_model.assert_called_once()
                call_kwargs = mock_user_model.call_args[1]
                assert call_kwargs['is_active'] is True
                assert call_kwargs['is_verified'] is False


class TestUserServiceUpdate:
    """Unit tests for user update operations"""
    
    @pytest.fixture
    def user_service(self):
        mock_session = AsyncMock()
        return UserService(mock_session)
    
    @pytest.fixture
    def existing_user(self):
        return User(
            id="user-123",
            email="old@example.com",
            username="olduser"
        )
    
    async def test_update_user_success(self, user_service, existing_user):
        """Test successful user update"""
        update_data = UserUpdate(
            username="updated_user",
            email="updated@example.com"
        )
        
        with patch.object(user_service, 'get_user_by_id', return_value=existing_user):
            user_service.db.commit = AsyncMock()
            user_service.db.refresh = AsyncMock()
            
            result = await user_service.update_user("user-123", update_data)
            
            assert result == existing_user
            assert existing_user.username == "updated_user"
            assert existing_user.email == "updated@example.com"
    
    async def test_update_user_not_found(self, user_service):
        """Test updating non-existent user"""
        update_data = UserUpdate(username="updated_user")
        
        with patch.object(user_service, 'get_user_by_id', return_value=None):
            result = await user_service.update_user("nonexistent", update_data)
        
        assert result is None
    
    async def test_update_user_password_hashing(self, user_service, existing_user):
        """Test that password is hashed when updating password"""
        update_data = UserUpdate(password="new_password123")
        
        with patch.object(user_service, 'get_user_by_id', return_value=existing_user):
            with patch('app.services.user.get_password_hash') as mock_hash:
                mock_hash.return_value = "hashed_new_password"
                
                user_service.db.commit = AsyncMock()
                user_service.db.refresh = AsyncMock()
                
                await user_service.update_user("user-123", update_data)
                
                mock_hash.assert_called_once_with("new_password123")
                assert existing_user.password_hash == "hashed_new_password"
    
    async def test_update_user_partial_update(self, user_service, existing_user):
        """Test partial user update with exclude_unset"""
        update_data = UserUpdate(username="updated_user")
        
        with patch.object(user_service, 'get_user_by_id', return_value=existing_user):
            user_service.db.commit = AsyncMock()
            user_service.db.refresh = AsyncMock()
            
            result = await user_service.update_user("user-123", update_data)
            
            assert result.username == "updated_user"
            # Other fields should remain unchanged
            assert result.email == "old@example.com"


class TestUserServiceAuthentication:
    """Unit tests for user authentication"""
    
    @pytest.fixture
    def user_service(self):
        mock_session = AsyncMock()
        return UserService(mock_session)
    
    @pytest.fixture
    def user_with_password(self):
        return User(
            id="user-123",
            email="test@example.com",
            username="testuser",
            password_hash="hashed_correct_password"
        )
    
    async def test_authenticate_user_success(self, user_service, user_with_password):
        """Test successful user authentication"""
        with patch.object(user_service, 'get_user_by_email', return_value=user_with_password):
            with patch('app.services.user.verify_password', return_value=True):
                result = await user_service.authenticate_user("test@example.com", "correct_password")
            
            assert result == user_with_password
    
    async def test_authenticate_user_wrong_password(self, user_service, user_with_password):
        """Test authentication with wrong password"""
        with patch.object(user_service, 'get_user_by_email', return_value=user_with_password):
            with patch('app.services.user.verify_password', return_value=False):
                result = await user_service.authenticate_user("test@example.com", "wrong_password")
            
            assert result is None
    
    async def test_authenticate_user_not_found(self, user_service):
        """Test authentication for non-existent user"""
        with patch.object(user_service, 'get_user_by_email', return_value=None):
            result = await user_service.authenticate_user("nonexistent@example.com", "any_password")
        
        assert result is None
    
    async def test_authenticate_user_empty_email(self, user_service):
        """Test authentication with empty email"""
        with patch.object(user_service, 'get_user_by_email', return_value=None):
            result = await user_service.authenticate_user("", "password")
        
        assert result is None


class TestUserServiceDeactivationDeletion:
    """Unit tests for user deactivation and deletion"""
    
    @pytest.fixture
    def user_service(self):
        mock_session = AsyncMock()
        return UserService(mock_session)
    
    @pytest.fixture
    def active_user(self):
        return User(
            id="user-123",
            email="test@example.com",
            is_active=True
        )
    
    async def test_deactivate_user_success(self, user_service, active_user):
        """Test successful user deactivation"""
        with patch.object(user_service, 'get_user_by_id', return_value=active_user):
            user_service.db.commit = AsyncMock()
            
            result = await user_service.deactivate_user("user-123")
            
            assert result is True
            assert active_user.is_active is False
            user_service.db.commit.assert_called_once()
    
    async def test_deactivate_user_not_found(self, user_service):
        """Test deactivating non-existent user"""
        with patch.object(user_service, 'get_user_by_id', return_value=None):
            result = await user_service.deactivate_user("nonexistent")
        
        assert result is False
    
    async def test_delete_user_success(self, user_service, active_user):
        """Test successful user deletion"""
        with patch.object(user_service, 'get_user_by_id', return_value=active_user):
            user_service.db.delete = AsyncMock()
            user_service.db.commit = AsyncMock()
            
            result = await user_service.delete_user("user-123")
            
            assert result is True
            user_service.db.delete.assert_called_once_with(active_user)
            user_service.db.commit.assert_called_once()
    
    async def test_delete_user_not_found(self, user_service):
        """Test deleting non-existent user"""
        with patch.object(user_service, 'get_user_by_id', return_value=None):
            result = await user_service.delete_user("nonexistent")
        
        assert result is False


class TestUserServiceEdgeCases:
    """Unit tests for edge cases and error scenarios"""
    
    @pytest.fixture
    def user_service(self):
        mock_session = AsyncMock()
        return UserService(mock_session)
    
    async def test_database_error_handling(self, user_service):
        """Test handling of database errors"""
        user_service.db.execute = AsyncMock(side_effect=Exception("Database connection error"))
        
        with pytest.raises(Exception):
            await user_service.get_user_by_id("user-123")
    
    async def test_empty_string_queries(self, user_service):
        """Test queries with empty strings"""
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = None
        user_service.db.execute = AsyncMock(return_value=mock_result)
        
        # These should not crash and should return None
        assert await user_service.get_user_by_email("") is None
        assert await user_service.get_user_by_username("") is None
    
    async def test_whitespace_email_handling(self, user_service):
        """Test handling of email with whitespace"""
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = None
        user_service.db.execute = AsyncMock(return_value=mock_result)
        
        result = await user_service.get_user_by_email("  test@example.com  ")
        
        assert result is None
        user_service.db.execute.assert_called_once()
    
    def test_password_security_requirements(self):
        """Test password security considerations"""
        # This tests security considerations around password handling
        weak_passwords = ["", "123", "password", "abc"]
        strong_passwords = ["StrongPass123!", "MySecure$Password2023"]
        
        # Basic password strength validation
        for password in weak_passwords:
            is_weak = len(password) < 8 or password.lower() in ["password", "123456", "abc"]
            assert is_weak
        
        for password in strong_passwords:
            has_length = len(password) >= 8
            has_mixed_case = any(c.isupper() for c in password) and any(c.islower() for c in password)
            has_number = any(c.isdigit() for c in password)
            has_special = any(c in "!@#$%^&*()_+-=[]{}|;:,.<>?" for c in password)
            
            assert has_length
            assert has_mixed_case or has_number or has_special  # At least some complexity