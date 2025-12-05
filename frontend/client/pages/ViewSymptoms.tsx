import { useState, useEffect } from 'react';
import { useNavigate, useParams } from 'react-router-dom';
import { Button } from '../components/ui/button';
import { toast } from 'sonner';
import { Heart, ArrowLeft, Loader2, Calendar, AlertCircle } from 'lucide-react';
import { Pet, Symptom } from '../../shared/api';
import { api_v, base_url } from '../lib/utils';

export default function ViewSymptoms() {
  const { petId } = useParams<{ petId: string }>();
  const navigate = useNavigate();
  const [pet, setPet] = useState<Pet | null>(null);
  const [symptoms, setSymptoms] = useState<Symptom[]>([]);
  const [isLoading, setIsLoading] = useState(true);

  const severityColors = {
    mild: 'bg-yellow-50 border-yellow-200 text-yellow-900',
    moderate: 'bg-orange-50 border-orange-200 text-orange-900',
    severe: 'bg-red-50 border-red-200 text-red-900',
  };

  const severityBadgeColors = {
    mild: 'bg-yellow-100 text-yellow-800',
    moderate: 'bg-orange-100 text-orange-800',
    severe: 'bg-red-100 text-red-800',
  };

  useEffect(() => {
    fetchPetAndSymptoms();
  }, [petId]);

  const fetchPetAndSymptoms = async () => {
    try {
      setIsLoading(true);
      const token = localStorage.getItem('authToken');

      const [petRes, symptomsRes] = await Promise.all([
        fetch(`${base_url}${api_v}pets/${petId}`, {
            method: 'GET',
            headers: { 'Authorization': `Bearer ${token}` },
        }),
        fetch(`${base_url}${api_v}symptoms/pet/${petId}`, {
            method: 'GET',
            headers: { 'Authorization': `Bearer ${token}` },
        }),
      ]);

      if (!petRes.ok) throw new Error('Failed to fetch pet');

      const petData: Pet = await petRes.json();
      setPet(petData);

      if (symptomsRes.ok) {
        const symptomsData: Symptom[] = await symptomsRes.json();
        setSymptoms(symptomsData);
      }
    } catch (error) {
      toast.error('Failed to load symptoms');
      navigate('/dashboard');
    } finally {
      setIsLoading(false);
    }
  };

  if (isLoading) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-green-50 via-white to-blue-50">
        <Loader2 className="h-8 w-8 animate-spin text-green-500" />
      </div>
    );
  }

  if (!pet) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-green-50 via-white to-blue-50 flex items-center justify-center">
        <div className="text-center">
          <h1 className="text-2xl font-bold text-gray-900 mb-4">Pet not found</h1>
          <Button onClick={() => navigate('/dashboard')} className="bg-gradient-to-r from-green-500 to-green-600">
            Back to Dashboard
          </Button>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-green-50 via-white to-blue-50">
      {/* Header */}
      <div className="bg-white border-b border-gray-200 sticky top-0 z-10">
        <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 py-4 flex items-center gap-4">
          <button
            onClick={() => navigate('/dashboard')}
            className="text-gray-600 hover:text-gray-900 hover:bg-gray-100 p-2 rounded-lg transition"
          >
            <ArrowLeft className="h-5 w-5" />
          </button>
          <div className="flex items-center gap-3">
            <div className="bg-gradient-to-br from-green-500 to-green-600 rounded-lg p-2">
              <Heart className="h-6 w-6 text-white fill-white" />
            </div>
            <h1 className="text-2xl font-bold text-gray-900">PetCare</h1>
          </div>
        </div>
      </div>

      {/* Main Content */}
      <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
        <div className="mb-8">
          <h2 className="text-3xl font-bold text-gray-900 mb-2">
            Symptom History for {pet.name}
          </h2>
          <p className="text-gray-600">
            {pet.species} • {pet.breed || 'Breed not specified'}
          </p>
        </div>

        {symptoms.length === 0 ? (
          <div className="bg-white rounded-2xl shadow-lg p-12 text-center border border-gray-100">
            <AlertCircle className="h-16 w-16 text-gray-300 mx-auto mb-4" />
            <h3 className="text-xl font-semibold text-gray-900 mb-2">No symptoms logged yet</h3>
            <p className="text-gray-600 mb-6">Start tracking {pet.name}'s health by logging symptoms</p>
            <Button
              onClick={() => navigate(`/pets/${petId}/symptoms`)}
              className="bg-gradient-to-r from-orange-500 to-orange-600 hover:from-orange-600 hover:to-orange-700 text-white font-semibold rounded-lg h-11 px-6"
            >
              Log Symptoms
            </Button>
          </div>
        ) : (
          <div className="space-y-4">
            {symptoms.map((symptom) => (
              <div
                key={symptom.id}
                className={`rounded-2xl p-6 border ${severityColors[symptom.severity]}`}
              >
                <div className="flex items-start justify-between mb-3">
                  <div className="flex-1">
                    <div className="flex items-center gap-3 mb-2">
                      <h3 className="text-lg font-bold">{symptom.symptom}</h3>
                      <span
                        className={`px-3 py-1 rounded-full text-sm font-semibold ${severityBadgeColors[symptom.severity]}`}
                      >
                        {symptom.severity.charAt(0).toUpperCase() + symptom.severity.slice(1)}
                      </span>
                    </div>
                  </div>
                </div>

                <div className="space-y-3 text-sm opacity-90">
                  <div className="flex items-center gap-3 text-gray-700">
                    <Calendar className="h-4 w-4" />
                    <span className="font-medium">Observed:</span>
                    <span>{symptom.observed_at ? new Date(symptom.observed_at).toLocaleString() : 'Unknown'}</span>
                    {typeof symptom.duration_hours === 'number' && (
                      <span className="ml-4 text-gray-600">• Duration: {symptom.duration_hours} hour{symptom.duration_hours === 1 ? '' : 's'}</span>
                    )}
                  </div>

                  {symptom.description ? (
                    <div className="mt-2 pt-2 border-t border-current border-opacity-10">
                      <p className="text-sm text-gray-800">{symptom.description}</p>
                    </div>
                  ) : null}

                  <div className="mt-2 text-xs text-gray-600">
                    <div><span className="font-medium">Severity:</span> {symptom.severity}</div>
                    <div><span className="font-medium">Recorded on:</span> {symptom.date ? new Date(symptom.date).toLocaleString() : '—'}</div>
                  </div>
                </div>
              </div>
            ))}
          </div>
        )}

        {/* Action Buttons */}
        <div className="mt-8 flex gap-4">
          <Button
            onClick={() => navigate(`/pets/${petId}/log-symptoms`)}
            className="flex-1 bg-gradient-to-r from-orange-500 to-orange-600 hover:from-orange-600 hover:to-orange-700 text-white font-semibold rounded-lg h-11"
          >
            Log New Symptoms
          </Button>
          <Button
            onClick={() => navigate('/dashboard')}
            variant="outline"
            className="flex-1 border-gray-200 text-gray-700 hover:bg-gray-50 font-semibold"
          >
            Back to Dashboard
          </Button>
        </div>
      </div>
    </div>
  );
}
