import { useState, useEffect } from 'react';
import { useNavigate, useParams } from 'react-router-dom';
import { Button } from '../components/ui/button';
import { toast } from 'sonner';
import { Heart, ArrowLeft, Loader2, AlertCircle, Activity } from 'lucide-react';
import { Pet, Symptom } from '../../shared/api';

interface SymptomAssessment {
  id: string;
  pet_id: string;
  symptoms_json: Record<string, any>;
  ai_analysis: string;
  urgency_level: string;
  recommendations: string;
  possible_causes: string[];
  ai_provider: string;
  processing_time_ms: number;
  created_at: string;
}

export default function AIPetAdvisor() {
  const { petId } = useParams<{ petId: string }>();
  const navigate = useNavigate();
  const [pet, setPet] = useState<Pet | null>(null);
  const [symptoms, setSymptoms] = useState<Symptom[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [assessment, setAssessment] = useState<SymptomAssessment | null>(null);

  useEffect(() => {
    fetchPetAndAnalyze();
  }, [petId]);

  const fetchPetAndAnalyze = async () => {
    try {
      setIsLoading(true);
      const token = localStorage.getItem('authToken');

      // Fetch pet and symptoms
      const [petRes, symptomsRes] = await Promise.all([
        fetch(`${base_url}${api_v}pets/${petId}`, {
          headers: { 'Authorization': `Bearer ${token}` },
          method: 'GET',
        }),
        fetch(`${base_url}${api_v}symptoms/pet/${petId}`, {
          headers: { 'Authorization': `Bearer ${token}` },
          method: 'GET',
        }),
      ]);

      if (!petRes.ok) throw new Error('Failed to fetch pet');

      const petData: Pet = await petRes.json();
      setPet(petData);

      if (symptomsRes.ok) {
        const symptomsData: Symptom[] = await symptomsRes.json();
        setSymptoms(symptomsData);

        // If there are symptoms, automatically call the assessment endpoint
        if (symptomsData.length > 0) {
          const assessmentRes = await fetch(`${base_url}${api_v}symptoms/assess`, {
            method: 'POST',
            headers: {
              'Content-Type': 'application/json',
              'Authorization': `Bearer ${token}`,
            },
            body: JSON.stringify({
              pet_id: petId,
            }),
          });

          if (assessmentRes.ok) {
            const assessmentData: SymptomAssessment = await assessmentRes.json();
            setAssessment(assessmentData);
          } else {
            toast.error('Failed to generate AI assessment');
          }
        }
      }
    } catch (error) {
      console.error('Error:', error);
      toast.error('Failed to load pet information');
      navigate('/dashboard');
    } finally {
      setIsLoading(false);
    }
  };

  const getUrgencyColor = (level: string) => {
    switch (level.toLowerCase()) {
      case 'emergency':
        return 'bg-red-100 text-red-800 border-red-200';
      case 'high':
        return 'bg-orange-100 text-orange-800 border-orange-200';
      case 'medium':
        return 'bg-yellow-100 text-yellow-800 border-yellow-200';
      case 'low':
        return 'bg-green-100 text-green-800 border-green-200';
      default:
        return 'bg-gray-100 text-gray-800 border-gray-200';
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
            AI Health Assessment for {pet.name}
          </h2>
          <p className="text-gray-600">
            AI-powered analysis of your pet's symptoms
          </p>
        </div>

        {symptoms.length === 0 ? (
          <div className="bg-white rounded-2xl shadow-lg p-12 text-center border border-gray-100">
            <div className="w-16 h-16 bg-blue-100 rounded-full flex items-center justify-center mx-auto mb-4">
              <Activity className="h-8 w-8 text-blue-600" />
            </div>
            <h4 className="text-lg font-semibold text-gray-900 mb-2">
              No Symptoms Recorded
            </h4>
            <p className="text-gray-600 mb-6">
              {pet.name} doesn't have any symptoms logged yet. Add symptoms to get an AI-powered health assessment.
            </p>
            <Button
              onClick={() => navigate(`/pets/${petId}/symptoms`)}
              className="bg-gradient-to-r from-green-500 to-green-600 hover:from-green-600 hover:to-green-700 text-white font-semibold rounded-lg h-11"
            >
              Log Symptoms
            </Button>
          </div>
        ) : !assessment ? (
          <div className="bg-white rounded-2xl shadow-lg p-12 text-center border border-gray-100">
            <Loader2 className="h-12 w-12 animate-spin text-green-500 mx-auto mb-4" />
            <h4 className="text-lg font-semibold text-gray-900 mb-2">
              Analyzing Symptoms...
            </h4>
            <p className="text-gray-600">
              Our AI is reviewing {pet.name}'s symptoms
            </p>
          </div>
        ) : (
          <div className="space-y-6">
            {/* Disclaimer */}
            <div className="bg-amber-50 border border-amber-200 rounded-xl p-4 flex gap-3">
              <AlertCircle className="h-5 w-5 text-amber-600 flex-shrink-0 mt-0.5" />
              <div>
                <p className="text-sm font-medium text-amber-900">
                  Medical Disclaimer
                </p>
                <p className="text-sm text-amber-800 mt-1">
                  This is AI-generated information for reference only. Always consult with a veterinarian for proper diagnosis and treatment.
                </p>
              </div>
            </div>

            {/* Urgency Level */}
            <div className={`rounded-xl p-6 border-2 ${getUrgencyColor(assessment.urgency_level)}`}>
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm font-medium uppercase tracking-wide mb-1">Urgency Level</p>
                  <p className="text-2xl font-bold capitalize">{assessment.urgency_level}</p>
                </div>
                <div className="text-sm text-gray-600">
                  Analyzed {symptoms.length} symptom{symptoms.length !== 1 ? 's' : ''}
                </div>
              </div>
            </div>

            {/* Symptoms Analyzed */}
            <div className="bg-white rounded-2xl shadow-lg p-6 border border-gray-100">
              <h4 className="text-lg font-bold text-gray-900 mb-4">
                Symptoms Analyzed
              </h4>
              <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
                {symptoms.map((symptom) => (
                  <div
                    key={symptom.id}
                    className="flex items-center gap-3 p-3 bg-gray-50 rounded-lg border border-gray-100"
                  >
                    <div className="w-2 h-2 rounded-full bg-green-500"></div>
                    <div className="flex-1">
                      <p className="font-medium text-gray-900">{symptom.symptom}</p>
                      <p className="text-sm text-gray-600 capitalize">{symptom.severity} severity</p>
                    </div>
                  </div>
                ))}
              </div>
            </div>

            {/* AI Analysis */}
            <div className="bg-white rounded-2xl shadow-lg p-8 border border-gray-100">
              <h4 className="text-lg font-bold text-gray-900 mb-4">
                AI Analysis
              </h4>
              <div className="prose prose-sm max-w-none text-gray-700">
                <p className="whitespace-pre-wrap">{assessment.ai_analysis}</p>
              </div>
            </div>

            {/* Possible Causes */}
            {assessment.possible_causes && assessment.possible_causes.length > 0 && (
              <div className="bg-white rounded-2xl shadow-lg p-8 border border-gray-100">
                <h4 className="text-lg font-bold text-gray-900 mb-4">
                  Possible Causes
                </h4>
                <ul className="space-y-3">
                  {assessment.possible_causes.map((cause, index) => (
                    <li key={index} className="flex gap-3">
                      <div className="w-6 h-6 rounded-full bg-purple-100 text-purple-600 flex items-center justify-center flex-shrink-0 text-sm font-semibold">
                        {index + 1}
                      </div>
                      <span className="text-gray-700">{cause}</span>
                    </li>
                  ))}
                </ul>
              </div>
            )}

            {/* Recommendations */}
            {assessment.recommendations && (
              <div className="bg-white rounded-2xl shadow-lg p-8 border border-gray-100">
                <h4 className="text-lg font-bold text-gray-900 mb-4">
                  Recommendations
                </h4>
                <div className="prose prose-sm max-w-none text-gray-700">
                  <p className="whitespace-pre-wrap">{assessment.recommendations}</p>
                </div>
              </div>
            )}

            {/* Action Buttons */}
            <div className="flex gap-4">
              <Button
                onClick={() => navigate(`/pets/${petId}/symptoms`)}
                className="flex-1 bg-gradient-to-r from-orange-500 to-orange-600 hover:from-orange-600 hover:to-orange-700 text-white font-semibold rounded-lg h-11"
              >
                Log New Symptoms
              </Button>
              <Button
                onClick={() => navigate('/dashboard')}
                variant="outline"
                className="flex-1 border-gray-200 text-gray-700 hover:bg-gray-50 font-semibold rounded-lg h-11"
              >
                Back to Dashboard
              </Button>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}

// Import Label, base_url
import { api_v, base_url } from '../lib/utils';

