import { useState, useEffect } from 'react';
import { useNavigate, useParams } from 'react-router-dom';
import { Button } from '../components/ui/button';
import { Input } from '../components/ui/input';
import { Label } from '../components/ui/label';
import { toast } from 'sonner';
import { Heart, ArrowLeft, Loader2, X } from 'lucide-react';
import { Pet, SymptomEntry } from '../../shared/api';

interface SymptomInput extends SymptomEntry {
  id: string;
  symptom: string;
  severity: 'mild' | 'moderate' | 'severe';
  description: string;
  observed_at: string;
  duration_hours: number;
}

export default function LogSymptoms() {
  const { petId } = useParams<{ petId: string }>();
  const navigate = useNavigate();
  const [pet, setPet] = useState<Pet | null>(null);
  const [isLoadingPet, setIsLoadingPet] = useState(true);
  const [isSubmitting, setIsSubmitting] = useState(false);

  const [symptoms, setSymptoms] = useState<SymptomInput[]>([
    { 
      id: '1', 
      symptom: '', 
      severity: 'mild',
      description: '',
      observed_at: '',
      duration_hours: 0,
    },
  ]);
  const [notes, setNotes] = useState('');

  const commonSymptoms = [
    'Coughing',
    'Vomiting',
    'Diarrhea',
    'Lethargy',
    'Loss of Appetite',
    'Excessive Thirst',
    'Scratching',
    'Limping',
    'Sneezing',
    'Eye Discharge',
    'Ear Infections',
    'Skin Rash',
  ];

  useEffect(() => {
    fetchPet();
  }, [petId]);

  const fetchPet = async () => {
    try {
      setIsLoadingPet(true);
      const response = await fetch(`${base_url}${api_v}pets/${petId}`, {
        method: 'GET',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${localStorage.getItem('authToken')}`,
        },
      });

      if (!response.ok) throw new Error('Failed to fetch pet');

      const data: Pet = await response.json();
      setPet(data);
    } catch (error) {
      toast.error('Failed to load pet information');
      navigate('/dashboard');
    } finally {
      setIsLoadingPet(false);
    }
  };

  const handleAddSymptom = () => {
    setSymptoms([
      ...symptoms,
      {
        id: Date.now().toString(),
        symptom: '',
        severity: 'mild',
        description: '',
        observed_at: '',
        duration_hours: 0,
      },
    ]);
  };

  const handleRemoveSymptom = (id: string) => {
    if (symptoms.length > 1) {
      setSymptoms(symptoms.filter((s) => s.id !== id));
    }
  };

  const handleSymptomChange = (id: string, field: string, value: string) => {
    setSymptoms(
      symptoms.map((s) =>
        s.id === id ? { ...s, [field]: value } : s
      )
    );
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();

    const filledSymptoms = symptoms.filter((s) => s.symptom.trim());
    if (filledSymptoms.length === 0) {
      toast.error('Please add at least one symptom');
      return;
    }

    setIsSubmitting(true);

    try {
      filledSymptoms.map(async (s) => {
        if (!s.symptom || !s.severity || !s.observed_at) {
          throw new Error('Please fill out all required symptom fields');
        }
        const response = await fetch(`${base_url}${api_v}symptoms`, {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
            'Authorization': `Bearer ${localStorage.getItem('authToken')}`,
          },
          body: JSON.stringify({
            symptom_name: s.symptom,
            severity: s.severity,
            description: s.description,
            observed_at: s.observed_at,
            duration_hours: s.duration_hours,
            pet_id: petId,
          }),
        });

        if (!response.ok) throw new Error('Failed to log symptoms');
      });

      toast.success('Symptoms logged successfully!');
      navigate('/dashboard');
    } catch (error) {
      toast.error('Failed to log symptoms');
    } finally {
      setIsSubmitting(false);
    }
  };

  if (isLoadingPet) {
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
            Log Symptoms for {pet.name}
          </h2>
          <p className="text-gray-600">
            {pet.species} • {pet.breed || 'Breed not specified'}
          </p>
        </div>

        {/* Form */}
        <div className="bg-white rounded-2xl shadow-lg p-8 border border-gray-100">
          <form onSubmit={handleSubmit} className="space-y-8">
            {/* Symptoms List */}
            <div className="space-y-6">
              <div>
                <h3 className="text-xl font-bold text-gray-900 mb-4">
                  Symptoms
                </h3>
                <p className="text-gray-600 mb-6">
                  Add one or more symptoms you've observed
                </p>
              </div>

              {symptoms.map((symptom, index) => (
                <div key={symptom.id} className="bg-gray-50 rounded-xl p-6 border border-gray-200">
                  <div className="flex items-start justify-between mb-4">
                    <h4 className="font-medium text-gray-900">Symptom #{index + 1}</h4>
                    {symptoms.length > 1 && (
                      <button
                        type="button"
                        onClick={() => handleRemoveSymptom(symptom.id)}
                        className="text-red-500 hover:text-red-600 hover:bg-red-50 p-1 rounded-lg transition"
                      >
                        <X className="h-5 w-5" />
                      </button>
                    )}
                  </div>

                  <div className="space-y-4">
                    <div className="space-y-2">
                      <Label htmlFor={`symptom-${symptom.id}`} className="text-gray-700 font-medium">
                        Symptom Name
                      </Label>
                      <input
                        id={`symptom-${symptom.id}`}
                        list={`symptom-suggestions`}
                        placeholder="e.g., Coughing, Vomiting..."
                        value={symptom.symptom}
                        onChange={(e) =>
                          handleSymptomChange(symptom.id, 'symptom', e.target.value)
                        }
                        className="w-full px-4 py-2 border border-gray-200 rounded-lg text-gray-900 focus:border-green-500 focus:ring-green-500"
                      />
                      <datalist id={`symptom-suggestions`}>
                        {commonSymptoms.map((s) => (
                          <option key={s} value={s} />
                        ))}
                      </datalist>
                    </div>

                    <div className="space-y-2">
                      <Label htmlFor={`severity-${symptom.id}`} className="text-gray-700 font-medium">
                        Severity
                      </Label>
                      <select
                        id={`severity-${symptom.id}`}
                        value={symptom.severity}
                        onChange={(e) =>
                          handleSymptomChange(
                            symptom.id,
                            'severity',
                            e.target.value
                          )
                        }
                        className="w-full px-4 py-2 border border-gray-200 rounded-lg text-gray-900 focus:border-green-500 focus:ring-green-500"
                      >
                        <option value="mild">Mild</option>
                        <option value="moderate">Moderate</option>
                        <option value="severe">Severe</option>
                      </select>
                    </div>

                    <div className="space-y-2">
                      <Label htmlFor={`description-${symptom.id}`} className="text-gray-700 font-medium">
                        Description
                      </Label>
                      <input
                        type="text"
                        id={`description-${symptom.id}`}
                        value={symptom.description}
                        onChange={(e) =>
                          handleSymptomChange(
                            symptom.id,
                            'description',
                            e.target.value
                          )
                        }
                        className="w-full px-4 py-2 border border-gray-200 rounded-lg text-gray-900 focus:border-green-500 focus:ring-green-500"
                      />
                    </div>

                    <div className="space-y-2">
                      <Label htmlFor={`observed_at-${symptom.id}`} className="text-gray-700 font-medium">
                        Observed At
                      </Label>
                      <input
                        type="datetime-local"
                        id={`observed_at-${symptom.id}`}
                        value={symptom.observed_at}
                        onChange={(e) =>
                          handleSymptomChange(
                            symptom.id,
                            'observed_at',
                            e.target.value
                          )
                        }
                        className="w-full px-4 py-2 border border-gray-200 rounded-lg text-gray-900 focus:border-green-500 focus:ring-green-500"
                      />
                    </div>

                    <div className="space-y-2">
                      <Label htmlFor={`duration_hours-${symptom.id}`} className="text-gray-700 font-medium">
                        Duration Hours
                      </Label>
                      <input
                        type="number"
                        id={`duration_hours-${symptom.id}`}
                        value={symptom.duration_hours}
                        onChange={(e) =>
                          handleSymptomChange(
                            symptom.id,
                            'duration_hours',
                            e.target.value
                          )
                        }
                        className="w-full px-4 py-2 border border-gray-200 rounded-lg text-gray-900 focus:border-green-500 focus:ring-green-500"
                      />
                    </div>
                  </div>
                </div>
              ))}

              <Button
                type="button"
                onClick={handleAddSymptom}
                variant="outline"
                className="w-full border-dashed border-green-200 text-green-600 hover:bg-green-50 font-semibold h-11"
              >
                <Plus className="h-5 w-5 mr-2" />
                Add Another Symptom
              </Button>
            </div>

            {/* Notes */}
            <div className="space-y-2">
              <Label htmlFor="notes" className="text-gray-700 font-medium">
                Additional Notes (Optional)
              </Label>
              <textarea
                id="notes"
                placeholder="Any additional details about the symptoms or your pet's condition..."
                value={notes}
                onChange={(e) => setNotes(e.target.value)}
                rows={4}
                className="w-full px-4 py-2 border border-gray-200 rounded-lg text-gray-900 focus:border-green-500 focus:ring-green-500 resize-none"
              />
            </div>

            {/* Buttons */}
            <div className="flex gap-4">
              <Button
                type="submit"
                disabled={isSubmitting}
                className="flex-1 bg-gradient-to-r from-green-500 to-green-600 hover:from-green-600 hover:to-green-700 text-white font-semibold rounded-lg h-11"
              >
                {isSubmitting ? (
                  <>
                    <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                    Logging...
                  </>
                ) : (
                  'Log Symptoms'
                )}
              </Button>
              <Button
                type="button"
                onClick={() => navigate('/dashboard')}
                variant="outline"
                className="flex-1 border-gray-200 text-gray-700 hover:bg-gray-50 font-semibold"
              >
                Cancel
              </Button>
            </div>
          </form>
        </div>
      </div>
    </div>
  );
}

// Import Plus icon
import { Plus } from 'lucide-react';import { api_v, base_url } from '../lib/utils';

