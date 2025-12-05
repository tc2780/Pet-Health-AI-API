import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import { Button } from '../components/ui/button';
import { Input } from '../components/ui/input';
import { Label } from '../components/ui/label';
import { toast } from 'sonner';
import { Heart, LogOut, Plus, Loader2, Edit2, Trash2 } from 'lucide-react';
import { Pet } from '../../shared/api';
import { api_v, base_url } from '../lib/utils';

export default function Dashboard() {
  const [pets, setPets] = useState<Pet[]>([]);
  const [isLoadingPets, setIsLoadingPets] = useState(true);
  const [showAddPet, setShowAddPet] = useState(false);
  const [isSubmitting, setIsSubmitting] = useState(false);

  const [formData, setFormData] = useState({
    name: '',
    species: '',
    breed: '',
    age: '',
  });

  const { user, logout } = useAuth();
  const navigate = useNavigate();

  useEffect(() => {
    fetchPets();
  }, []);

  const fetchPets = async () => {
    try {
      setIsLoadingPets(true);
      const response = await fetch(`${base_url}${api_v}pets`, {
        method: 'GET',
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('authToken')}`,
        },
      });

      if (!response.ok) throw new Error('Failed to fetch pets');

      const data: Pet[] = await response.json();
      setPets(data);
    } catch (error) {
      toast.error('Failed to load pets');
    } finally {
      setIsLoadingPets(false);
    }
  };

  const handleAddPet = async (e: React.FormEvent) => {
    e.preventDefault();
    setIsSubmitting(true);

    try {
      const response = await fetch(`${base_url}${api_v}pets`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${localStorage.getItem('authToken')}`,
        },
        body: JSON.stringify({
          name: formData.name,
          species: formData.species,
          breed: formData.breed || undefined,
          age_years: formData.age ? parseInt(formData.age) : undefined,
        }),
      });

      if (!response.ok) throw new Error('Failed to add pet');

      const newPet: Pet = await response.json();
      setPets([...pets, newPet]);
      setFormData({ name: '', species: '', breed: '', age: '' });
      setShowAddPet(false);
      toast.success('Pet added successfully!');
    } catch (error) {
      toast.error('Failed to add pet');
    } finally {
      setIsSubmitting(false);
    }
  };

  const handleDeletePet = async (petId: string) => {
    try {
      const response = await fetch(`${base_url}${api_v}pets/${petId}`, {
        method: 'DELETE',
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('authToken')}`,
        },
      });

      if (!response.ok) throw new Error('Failed to delete pet');

      setPets(pets.filter(p => p.id !== petId));
      toast.success('Pet deleted successfully');
    } catch (error) {
      toast.error('Failed to delete pet');
    }
  };

  const handleLogout = () => {
    logout();
    navigate('/login');
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-green-50 via-white to-blue-50">
      {/* Header */}
      <div className="bg-white border-b border-gray-200 sticky top-0 z-10">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-4 flex items-center justify-between">
          <div className="flex items-center gap-3">
            <div className="bg-gradient-to-br from-green-500 to-green-600 rounded-lg p-2">
              <Heart className="h-6 w-6 text-white fill-white" />
            </div>
            <h1 className="text-2xl font-bold text-gray-900">PetCare</h1>
          </div>

          <div className="flex items-center gap-4">
            <span className="text-gray-700 font-medium">Welcome, {user?.name}</span>
            <Button
              onClick={handleLogout}
              variant="ghost"
              className="text-gray-600 hover:text-gray-900 hover:bg-gray-100"
            >
              <LogOut className="h-5 w-5 mr-2" />
              Logout
            </Button>
          </div>
        </div>
      </div>

      {/* Main Content */}
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
        {/* Welcome Section */}
        <div className="mb-12">
          <h2 className="text-3xl font-bold text-gray-900 mb-2">Your Pets</h2>
          <p className="text-gray-600">Manage your pets and track their health</p>
        </div>

        {/* Add Pet Button */}
        <div className="mb-8">
          <Button
            onClick={() => setShowAddPet(!showAddPet)}
            className="bg-gradient-to-r from-green-500 to-green-600 hover:from-green-600 hover:to-green-700 text-white font-semibold rounded-lg h-11"
          >
            <Plus className="h-5 w-5 mr-2" />
            Add New Pet
          </Button>
        </div>

        {/* Add Pet Form */}
        {showAddPet && (
          <div className="bg-white rounded-2xl shadow-lg p-8 mb-12 border border-gray-100">
            <h3 className="text-xl font-bold text-gray-900 mb-6">Add a New Pet</h3>
            <form onSubmit={handleAddPet} className="space-y-5 max-w-md">
              <div className="space-y-2">
                <Label htmlFor="pet-name" className="text-gray-700 font-medium">
                  Pet Name *
                </Label>
                <Input
                  id="pet-name"
                  placeholder="e.g., Max"
                  value={formData.name}
                  onChange={(e) => setFormData({ ...formData, name: e.target.value })}
                  required
                  className="h-11 border-gray-200"
                />
              </div>

              <div className="space-y-2">
                <Label htmlFor="pet-species" className="text-gray-700 font-medium">
                  Species *
                </Label>
                <select
                  id="pet-species"
                  value={formData.species}
                  onChange={(e) => setFormData({ ...formData, species: e.target.value })}
                  required
                  className="w-full h-11 px-4 border border-gray-200 rounded-lg text-gray-900 focus:border-green-500 focus:ring-green-500"
                >
                  <option value="">Select species</option>
                  <option value="dog">Dog</option>
                  <option value="cat">Cat</option>
                  <option value="rabbit">Rabbit</option>
                  <option value="bird">Bird</option>
                  <option value="hamster">Hamster</option>
                  <option value="other">Other</option>
                </select>
              </div>

              <div className="space-y-2">
                <Label htmlFor="pet-breed" className="text-gray-700 font-medium">
                  Breed
                </Label>
                <Input
                  id="pet-breed"
                  placeholder="e.g., Golden Retriever"
                  value={formData.breed}
                  onChange={(e) => setFormData({ ...formData, breed: e.target.value })}
                  className="h-11 border-gray-200"
                />
              </div>

              <div className="space-y-2">
                <Label htmlFor="pet-age" className="text-gray-700 font-medium">
                  Age (years)
                </Label>
                <Input
                  id="pet-age"
                  type="number"
                  placeholder="e.g., 3"
                  value={formData.age}
                  onChange={(e) => setFormData({ ...formData, age: e.target.value })}
                  min="0"
                  className="h-11 border-gray-200"
                />
              </div>

              <div className="flex gap-3">
                <Button
                  type="submit"
                  disabled={isSubmitting}
                  className="flex-1 bg-gradient-to-r from-green-500 to-green-600 hover:from-green-600 hover:to-green-700 text-white font-semibold rounded-lg h-11"
                >
                  {isSubmitting ? (
                    <>
                      <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                      Adding...
                    </>
                  ) : (
                    'Add Pet'
                  )}
                </Button>
                <Button
                  type="button"
                  onClick={() => setShowAddPet(false)}
                  variant="outline"
                  className="flex-1 border-gray-200 text-gray-700 hover:bg-gray-50"
                >
                  Cancel
                </Button>
              </div>
            </form>
          </div>
        )}

        {/* Pets Grid */}
        {isLoadingPets ? (
          <div className="flex items-center justify-center py-12">
            <Loader2 className="h-8 w-8 animate-spin text-green-500" />
          </div>
        ) : pets.length === 0 ? (
          <div className="bg-white rounded-2xl shadow-lg p-12 text-center border border-gray-100">
            <Heart className="h-16 w-16 text-gray-300 mx-auto mb-4" />
            <h3 className="text-xl font-semibold text-gray-900 mb-2">No pets yet</h3>
            <p className="text-gray-600 mb-6">Add your first pet to get started tracking their health</p>
          </div>
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {pets.map((pet) => (
              <div
                key={pet.id}
                className="bg-white rounded-2xl shadow-lg overflow-hidden border border-gray-100 hover:shadow-xl transition-shadow"
              >
                {/* Pet Card Header */}
                <div className="bg-gradient-to-r from-green-500 to-green-600 px-6 py-4">
                  <h3 className="text-xl font-bold text-white">{pet.name}</h3>
                  <p className="text-green-100">{pet.species}</p>
                </div>

                {/* Pet Details */}
                <div className="p-6 space-y-3">
                  {pet.breed && (
                    <div>
                      <p className="text-sm text-gray-500">Breed</p>
                      <p className="text-gray-900 font-medium">{pet.breed}</p>
                    </div>
                  )}
                  {pet.age !== undefined && (
                    <div>
                      <p className="text-sm text-gray-500">Age</p>
                      <p className="text-gray-900 font-medium">{pet.age} years</p>
                    </div>
                  )}
                  <div>
                    <p className="text-sm text-gray-500">Added</p>
                    <p className="text-gray-900 font-medium">
                      {new Date(pet.createdAt).toLocaleDateString()}
                    </p>
                  </div>
                </div>

                {/* Actions */}
                <div className="px-6 pb-6 space-y-3">
                  <Button
                    onClick={() => navigate(`/pets/${pet.id}/log-symptoms`)}
                    className="w-full bg-gradient-to-r from-orange-500 to-orange-600 hover:from-orange-600 hover:to-orange-700 text-white font-semibold rounded-lg h-10"
                  >
                    Log Symptoms
                  </Button>
                  <Button
                    onClick={() => navigate(`/pets/${pet.id}/symptoms`)}
                    className="w-full bg-gradient-to-r from-orange-500 to-orange-600 hover:from-orange-600 hover:to-orange-700 text-white font-semibold rounded-lg h-10"
                  >
                    View Symptoms
                  </Button>
                  <Button
                    onClick={() => navigate(`/pets/${pet.id}/ai`)}
                    className="w-full bg-gradient-to-r from-purple-500 to-purple-600 hover:from-purple-600 hover:to-purple-700 text-white font-semibold rounded-lg h-10"
                  >
                    Ask AI
                  </Button>
                  <Button
                    onClick={() => navigate(`/pets/${pet.id}/view-assessments`)}
                    className="w-full bg-gradient-to-r from-purple-500 to-purple-600 hover:from-purple-600 hover:to-purple-700 text-white font-semibold rounded-lg h-10"
                  >
                    View AI Assessments
                  </Button>
                  <Button
                    onClick={() => handleDeletePet(pet.id)}
                    variant="outline"
                    className="w-full border-red-200 text-red-600 hover:bg-red-50 font-semibold"
                  >
                    <Trash2 className="h-4 w-4 mr-2" />
                    Delete
                  </Button>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}
