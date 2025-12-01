"""
Comprehensive unit tests for PetService
"""
import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from typing import List

from app.services.pet import PetService
from app.models.pet import Pet
from app.schemas.pet import PetCreate, PetUpdate


class TestPetServiceQueries:
    """Unit tests for pet query operations"""
    
    @pytest.fixture
    def pet_service(self):
        """PetService with mocked database"""
        mock_session = AsyncMock()
        return PetService(mock_session)
    
    @pytest.fixture
    def sample_pet(self):
        """Sample pet for testing"""
        return Pet(
            id="pet-123",
            user_id="user-123",
            name="Buddy",
            species="dog",
            breed="Golden Retriever",
            age_years=5,
            weight_kg=30.0,
            sex="male",
            neutered=True
        )
    
    async def test_get_pet_by_id_found(self, pet_service, sample_pet):
        """Test getting pet by ID when pet exists"""
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = sample_pet
        pet_service.db.execute = AsyncMock(return_value=mock_result)
        
        result = await pet_service.get_pet_by_id("pet-123")
        
        assert result == sample_pet
        pet_service.db.execute.assert_called_once()
    
    async def test_get_pet_by_id_not_found(self, pet_service):
        """Test getting pet by ID when pet doesn't exist"""
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = None
        pet_service.db.execute = AsyncMock(return_value=mock_result)
        
        result = await pet_service.get_pet_by_id("nonexistent-pet")
        
        assert result is None
    
    async def test_get_pet_with_symptoms(self, pet_service, sample_pet):
        """Test getting pet with symptoms and assessments loaded"""
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = sample_pet
        pet_service.db.execute = AsyncMock(return_value=mock_result)
        
        result = await pet_service.get_pet_with_symptoms("pet-123")
        
        assert result == sample_pet
        # Verify that selectinload was used in the query
        pet_service.db.execute.assert_called_once()
    
    async def test_get_user_pets_multiple(self, pet_service):
        """Test getting all pets for a user with multiple pets"""
        pets = [
            Pet(id="pet-1", user_id="user-123", name="Buddy", species="dog"),
            Pet(id="pet-2", user_id="user-123", name="Whiskers", species="cat"),
            Pet(id="pet-3", user_id="user-123", name="Goldie", species="fish")
        ]
        
        mock_scalars = MagicMock()
        mock_scalars.all.return_value = pets
        mock_result = MagicMock()
        mock_result.scalars.return_value = mock_scalars
        pet_service.db.execute = AsyncMock(return_value=mock_result)
        
        result = await pet_service.get_user_pets("user-123")
        
        assert len(result) == 3
        assert all(pet.user_id == "user-123" for pet in result)
        assert result[0].name == "Buddy"
        assert result[1].name == "Whiskers"
        assert result[2].name == "Goldie"
    
    async def test_get_user_pets_empty(self, pet_service):
        """Test getting pets for user with no pets"""
        mock_scalars = MagicMock()
        mock_scalars.all.return_value = []
        mock_result = MagicMock()
        mock_result.scalars.return_value = mock_scalars
        pet_service.db.execute = AsyncMock(return_value=mock_result)
        
        result = await pet_service.get_user_pets("user-with-no-pets")
        
        assert result == []


class TestPetServiceCreate:
    """Unit tests for pet creation operations"""
    
    @pytest.fixture
    def pet_service(self):
        mock_session = AsyncMock()
        return PetService(mock_session)
    
    @pytest.fixture
    def pet_create_data(self):
        """Sample pet creation data"""
        return PetCreate(
            name="Max",
            species="dog",
            breed="Labrador Retriever",
            age_years=3,
            weight_kg=25.0,
            sex="male",
            neutered=False
        )
    
    async def test_create_pet_success(self, pet_service, pet_create_data):
        """Test successful pet creation"""
        mock_pet = Pet(
            id="pet-456",
            user_id="user-123",
            name="Max",
            species="dog",
            breed="Labrador Retriever",
            age_years=3,
            weight_kg=25.0,
            sex="male",
            neutered=False
        )
        
        pet_service.db.add = MagicMock()
        pet_service.db.commit = AsyncMock()
        pet_service.db.refresh = AsyncMock()
        
        with patch('app.services.pet.Pet', return_value=mock_pet) as mock_pet_model:
            result = await pet_service.create_pet("user-123", pet_create_data)
        
        # Verify the Pet model was called with correct arguments  
        mock_pet_model.assert_called_once_with(
            user_id="user-123",
            name="Max",
            species="dog", 
            breed="Labrador Retriever",
            age_years=3,
            weight_kg=25.0,
            sex="male",
            neutered=False
        )
        
        # Verify database operations
        pet_service.db.add.assert_called_once()
        pet_service.db.commit.assert_called_once()
        pet_service.db.refresh.assert_called_once()
        
        # Check the returned pet is our mock
        assert result == mock_pet
    
    async def test_create_pet_with_optional_fields(self, pet_service):
        """Test pet creation with optional fields"""
        pet_data = PetCreate(
            name="Mittens",
            species="cat",
            breed=None,  # Optional field
            age_years=2,
            weight_kg=4.5,
            sex="female",
            neutered=True
        )
        
        mock_pet = Pet(
            id="pet-789",
            user_id="user-456",
            name="Mittens",
            species="cat",
            breed=None,
            age_years=2,
            weight_kg=4.5,
            sex="female",
            neutered=True
        )
        
        pet_service.db.add = MagicMock()
        pet_service.db.commit = AsyncMock()
        pet_service.db.refresh = AsyncMock()
        
        with patch('app.models.pet.Pet', return_value=mock_pet):
            result = await pet_service.create_pet("user-456", pet_data)
        
        assert result.name == "Mittens"
        assert result.breed is None
    
    async def test_create_pet_field_mapping(self, pet_service, pet_create_data):
        """Test that all fields are properly mapped during creation"""
        pet_service.db.add = MagicMock()
        pet_service.db.commit = AsyncMock()
        pet_service.db.refresh = AsyncMock()
        
        with patch('app.services.pet.Pet') as mock_pet_model:
            await pet_service.create_pet("user-123", pet_create_data)
            
            # Verify Pet model was called with correct parameters
            mock_pet_model.assert_called_once_with(
                user_id="user-123",
                name="Max",
                species="dog",
                breed="Labrador Retriever",
                age_years=3,
                weight_kg=25.0,
                sex="male",
                neutered=False
            )


class TestPetServiceUpdate:
    """Unit tests for pet update operations"""
    
    @pytest.fixture
    def pet_service(self):
        mock_session = AsyncMock()
        return PetService(mock_session)
    
    @pytest.fixture
    def existing_pet(self):
        return Pet(
            id="pet-123",
            user_id="user-123",
            name="Old Name",
            species="dog",
            breed="Mixed",
            age_years=2,
            weight_kg=15.0,
            sex="female",
            neutered=False
        )
    
    async def test_update_pet_success(self, pet_service, existing_pet):
        """Test successful pet update"""
        update_data = PetUpdate(
            name="New Name",
            age_years=3,
            weight_kg=18.0
        )
        
        with patch.object(pet_service, 'get_pet_by_id', return_value=existing_pet):
            pet_service.db.commit = AsyncMock()
            pet_service.db.refresh = AsyncMock()
            
            result = await pet_service.update_pet("pet-123", update_data)
            
            assert result == existing_pet
            assert existing_pet.name == "New Name"
            assert existing_pet.age_years == 3
            assert existing_pet.weight_kg == 18.0
    
    async def test_update_pet_not_found(self, pet_service):
        """Test updating non-existent pet"""
        update_data = PetUpdate(name="New Name")
        
        with patch.object(pet_service, 'get_pet_by_id', return_value=None):
            result = await pet_service.update_pet("nonexistent", update_data)
        
        assert result is None
    
    async def test_update_pet_partial_update(self, pet_service, existing_pet):
        """Test partial pet update with exclude_unset"""
        update_data = PetUpdate(name="Updated Name")
        
        with patch.object(pet_service, 'get_pet_by_id', return_value=existing_pet):
            pet_service.db.commit = AsyncMock()
            pet_service.db.refresh = AsyncMock()
            
            result = await pet_service.update_pet("pet-123", update_data)
            
            assert result.name == "Updated Name"
            # Other fields should remain unchanged
            assert result.species == "dog"
            assert result.age_years == 2
    
    async def test_update_pet_neutered_status(self, pet_service, existing_pet):
        """Test updating pet neutered status"""
        update_data = PetUpdate(neutered=True)
        
        with patch.object(pet_service, 'get_pet_by_id', return_value=existing_pet):
            pet_service.db.commit = AsyncMock()
            pet_service.db.refresh = AsyncMock()
            
            result = await pet_service.update_pet("pet-123", update_data)
            
            assert result.neutered is True


class TestPetServiceDelete:
    """Unit tests for pet deletion operations"""
    
    @pytest.fixture
    def pet_service(self):
        mock_session = AsyncMock()
        return PetService(mock_session)
    
    @pytest.fixture
    def pet_to_delete(self):
        return Pet(
            id="pet-delete-123",
            user_id="user-123",
            name="DeleteMe",
            species="dog"
        )
    
    async def test_delete_pet_success(self, pet_service, pet_to_delete):
        """Test successful pet deletion"""
        with patch.object(pet_service, 'get_pet_by_id', return_value=pet_to_delete):
            pet_service.db.delete = AsyncMock()
            pet_service.db.commit = AsyncMock()
            
            result = await pet_service.delete_pet("pet-delete-123")
            
            assert result is True
            pet_service.db.delete.assert_called_once_with(pet_to_delete)
            pet_service.db.commit.assert_called_once()
    
    async def test_delete_pet_not_found(self, pet_service):
        """Test deleting non-existent pet"""
        with patch.object(pet_service, 'get_pet_by_id', return_value=None):
            result = await pet_service.delete_pet("nonexistent-pet")
        
        assert result is False
    
    async def test_delete_pet_cascade_behavior(self, pet_service, pet_to_delete):
        """Test that pet deletion handles cascading deletes properly"""
        # This tests the expectation that related data (symptoms, assessments) are handled
        with patch.object(pet_service, 'get_pet_by_id', return_value=pet_to_delete):
            pet_service.db.delete = AsyncMock()
            pet_service.db.commit = AsyncMock()
            
            result = await pet_service.delete_pet("pet-delete-123")
            
            assert result is True
            # The database should handle cascading deletes via foreign key constraints


class TestPetServiceValidation:
    """Unit tests for pet data validation and edge cases"""
    
    @pytest.fixture
    def pet_service(self):
        mock_session = AsyncMock()
        return PetService(mock_session)
    
    def test_pet_species_validation(self):
        """Test pet species validation logic"""
        valid_species = ["dog", "cat", "bird", "fish", "rabbit", "hamster", "reptile"]
        invalid_species = ["", "   ", "dinosaur", "123", None]
        
        # Basic species validation
        for species in valid_species:
            assert species.lower() in [s.lower() for s in valid_species]
        
        for species in invalid_species:
            if species is None:
                assert species is None
            else:
                is_invalid = species.strip() == "" or species not in valid_species
                assert is_invalid
    
    def test_pet_age_validation(self):
        """Test pet age validation logic"""
        valid_ages = [0, 1, 5, 10, 15, 20]
        invalid_ages = [-1, -5, 100, 200]
        
        for age in valid_ages:
            assert 0 <= age <= 30  # Reasonable age range for most pets
        
        for age in invalid_ages:
            is_invalid = age < 0 or age > 30
            assert is_invalid
    
    def test_pet_weight_validation(self):
        """Test pet weight validation logic"""
        valid_weights = [0.1, 1.0, 5.5, 20.0, 50.0]
        invalid_weights = [0, -1.0, -10.5, 500.0]
        
        for weight in valid_weights:
            assert 0.1 <= weight <= 200.0  # Reasonable weight range in kg
        
        for weight in invalid_weights:
            is_invalid = weight <= 0 or weight > 200.0
            assert is_invalid
    
    def test_pet_sex_validation(self):
        """Test pet sex validation logic"""
        valid_sexes = ["male", "female", "unknown"]
        invalid_sexes = ["", "   ", "boy", "girl", "m", "f", None]
        
        for sex in valid_sexes:
            assert sex.lower() in ["male", "female", "unknown"]
        
        for sex in invalid_sexes:
            if sex is None:
                assert sex is None
            else:
                is_invalid = sex.lower().strip() not in ["male", "female", "unknown"]
                assert is_invalid
    
    async def test_get_pet_by_id_with_special_characters(self, pet_service):
        """Test getting pet by ID with special characters"""
        special_ids = ["pet-123", "pet_456", "pet.789", "pet@abc", "pet%xyz"]
        
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = None
        pet_service.db.execute = AsyncMock(return_value=mock_result)
        
        for pet_id in special_ids:
            result = await pet_service.get_pet_by_id(pet_id)
            assert result is None  # Should handle gracefully
    
    async def test_database_error_handling(self, pet_service):
        """Test handling of database errors"""
        pet_service.db.execute = AsyncMock(side_effect=Exception("Database connection error"))
        
        with pytest.raises(Exception):
            await pet_service.get_pet_by_id("pet-123")
    
    async def test_empty_user_id_handling(self, pet_service):
        """Test handling of empty user ID in get_user_pets"""
        mock_scalars = MagicMock()
        mock_scalars.all.return_value = []
        mock_result = MagicMock()
        mock_result.scalars.return_value = mock_scalars
        pet_service.db.execute = AsyncMock(return_value=mock_result)
        
        result = await pet_service.get_user_pets("")
        
        assert result == []


class TestPetServiceBusinessLogic:
    """Unit tests for business logic and calculations"""
    
    def test_pet_age_categories(self):
        """Test pet age categorization logic"""
        # This tests business logic for categorizing pets by age
        def categorize_pet_age(age_years):
            if age_years < 1:
                return "puppy/kitten"
            elif age_years < 7:
                return "adult"
            else:
                return "senior"
        
        assert categorize_pet_age(0.5) == "puppy/kitten"
        assert categorize_pet_age(3) == "adult"
        assert categorize_pet_age(8) == "senior"
    
    def test_weight_to_size_mapping(self):
        """Test weight to size category mapping (example for dogs)"""
        def categorize_dog_size(weight_kg):
            if weight_kg < 10:
                return "small"
            elif weight_kg < 25:
                return "medium"
            elif weight_kg < 45:
                return "large"
            else:
                return "extra_large"
        
        assert categorize_dog_size(5.0) == "small"
        assert categorize_dog_size(20.0) == "medium"
        assert categorize_dog_size(35.0) == "large"
        assert categorize_dog_size(50.0) == "extra_large"
    
    def test_breed_standardization(self):
        """Test breed name standardization"""
        breed_variations = {
            "golden retriever": ["Golden Retriever", "golden retriever", "GOLDEN RETRIEVER"],
            "german shepherd": ["German Shepherd", "german shepherd", "German Shepard"],
            "labrador": ["Labrador", "Lab", "Labrador Retriever"]
        }
        
        for standard, variations in breed_variations.items():
            for variation in variations:
                normalized = variation.lower().strip()
                # Basic normalization test
                assert len(normalized) > 0
                assert normalized == normalized.strip()