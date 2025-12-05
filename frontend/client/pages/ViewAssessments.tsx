import { useState, useEffect } from 'react';
import { useNavigate, useParams } from 'react-router-dom';
import { Button } from '../components/ui/button';
import { toast } from 'sonner';
import { Heart, ArrowLeft, Loader2, Calendar, AlertCircle, Activity, Brain } from 'lucide-react';
import { Pet } from '../../shared/api';
import { api_v, base_url } from '../lib/utils';

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

export default function ViewAssessments() {
  const { petId } = useParams<{ petId: string }>();
  const navigate = useNavigate();
  const [pet, setPet] = useState<Pet | null>(null);
  const [assessments, setAssessments] = useState<SymptomAssessment[]>([]);
  const [isLoading, setIsLoading] = useState(true);

  const urgencyColors = {
    emergency: 'bg-red-50 border-red-200 text-red-900',
    high: 'bg-orange-50 border-orange-200 text-orange-900',
    medium: 'bg-yellow-50 border-yellow-200 text-yellow-900',
    low: 'bg-green-50 border-green-200 text-green-900',
  };

  const urgencyBadgeColors = {
    emergency: 'bg-red-100 text-red-800',
    high: 'bg-orange-100 text-orange-800',
    medium: 'bg-yellow-100 text-yellow-800',
    low: 'bg-green-100 text-green-800',
  };

  useEffect(() => {
    fetchPetAndAssessments();
  }, [petId]);

  const fetchPetAndAssessments = async () => {
    try {
      setIsLoading(true);
      const token = localStorage.getItem('authToken');

      const [petRes, assessmentsRes] = await Promise.all([
        fetch(`${base_url}${api_v}pets/${petId}`, {
          method: 'GET',
          headers: { 'Authorization': `Bearer ${token}` },
        }),
        fetch(`${base_url}${api_v}symptoms/assessments/pet/${petId}`, {
          method: 'GET',
          headers: { 'Authorization': `Bearer ${token}` },
        }),
      ]);

      if (!petRes.ok) throw new Error('Failed to fetch pet');

      const petData: Pet = await petRes.json();
      setPet(petData);

      if (assessmentsRes.ok) {
        const assessmentsData: SymptomAssessment[] = await assessmentsRes.json();
        setAssessments(assessmentsData);
      }
    } catch (error) {
      toast.error('Failed to load assessments');
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
            AI Assessments for {pet.name}
          </h2>
          <p className="text-gray-600">
            {pet.species} • {pet.breed || 'Breed not specified'}
          </p>
        </div>

        {assessments.length === 0 ? (
          <div className="bg-white rounded-2xl shadow-lg p-12 text-center border border-gray-100">
            <Brain className="h-16 w-16 text-gray-300 mx-auto mb-4" />
            <h3 className="text-xl font-semibold text-gray-900 mb-2">No assessments yet</h3>
            <p className="text-gray-600 mb-6">
              Log symptoms for {pet.name} to generate AI-powered health assessments
            </p>
            <Button
              onClick={() => navigate(`/pets/${petId}/log-symptoms`)}
              className="bg-gradient-to-r from-purple-500 to-purple-600 hover:from-purple-600 hover:to-purple-700 text-white font-semibold rounded-lg h-11 px-6"
            >
              Log Symptoms
            </Button>
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

            {assessments.map((assessment) => (
              <div
                key={assessment.id}
                className="bg-white rounded-2xl shadow-lg border border-gray-100 overflow-hidden"
              >
                {/* Header with urgency level */}
                <div className={`px-6 py-4 border-b ${urgencyColors[assessment.urgency_level as keyof typeof urgencyColors] || urgencyColors.low}`}>
                  <div className="flex items-center justify-between">
                    <div className="flex items-center gap-3">
                      <Activity className="h-5 w-5" />
                      <div>
                        <div className="flex items-center gap-3">
                          <span className="font-bold text-lg">Assessment</span>
                          <span
                            className={`px-3 py-1 rounded-full text-sm font-semibold ${urgencyBadgeColors[assessment.urgency_level as keyof typeof urgencyBadgeColors] || urgencyBadgeColors.low}`}
                          >
                            {assessment.urgency_level.charAt(0).toUpperCase() + assessment.urgency_level.slice(1)} Urgency
                          </span>
                        </div>
                        <div className="flex items-center gap-2 text-sm mt-1 opacity-80">
                          <Calendar className="h-4 w-4" />
                          <span>{new Date(assessment.created_at).toLocaleString()}</span>
                          <span className="ml-2">• {assessment.ai_provider || 'AI'}</span>
                        </div>
                      </div>
                    </div>
                  </div>
                </div>

                {/* Content */}
                <div className="p-6 space-y-6">
                  {/* AI Analysis */}
                  <div>
                    <h4 className="text-sm font-bold text-gray-900 uppercase tracking-wide mb-3 flex items-center gap-2">
                      <Brain className="h-4 w-4" />
                      AI Analysis
                    </h4>
                    <div className="prose prose-sm max-w-none text-gray-700">
                      <p className="whitespace-pre-wrap">{assessment.ai_analysis}</p>
                    </div>
                  </div>

                  {/* Possible Causes */}
                  {assessment.possible_causes && assessment.possible_causes.length > 0 && (
                    <div className="pt-4 border-t border-gray-100">
                      <h4 className="text-sm font-bold text-gray-900 uppercase tracking-wide mb-3">
                        Possible Causes
                      </h4>
                      <ul className="space-y-2">
                        {assessment.possible_causes.map((cause, index) => (
                          <li key={index} className="flex gap-3 text-sm text-gray-700">
                            <div className="w-5 h-5 rounded-full bg-purple-100 text-purple-600 flex items-center justify-center flex-shrink-0 text-xs font-semibold mt-0.5">
                              {index + 1}
                            </div>
                            <span>{cause}</span>
                          </li>
                        ))}
                      </ul>
                    </div>
                  )}

                  {/* Recommendations */}
                  {assessment.recommendations && (
                    <div className="pt-4 border-t border-gray-100">
                      <h4 className="text-sm font-bold text-gray-900 uppercase tracking-wide mb-3">
                        Recommendations
                      </h4>
                      <div className="prose prose-sm max-w-none text-gray-700">
                        <p className="whitespace-pre-wrap">{assessment.recommendations}</p>
                      </div>
                    </div>
                  )}

                  {/* Metadata */}
                  <div className="pt-4 border-t border-gray-100 text-xs text-gray-500 space-y-1">
                    {assessment.processing_time_ms && (
                      <div>Processing time: {assessment.processing_time_ms}ms</div>
                    )}
                    <div>Assessment ID: {assessment.id}</div>
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
            className="flex-1 bg-gradient-to-r from-purple-500 to-purple-600 hover:from-purple-600 hover:to-purple-700 text-white font-semibold rounded-lg h-11"
          >
            Generate New Assessment
          </Button>
          <Button
            onClick={() => navigate(`/pets/${petId}/symptoms`)}
            variant="outline"
            className="flex-1 border-gray-200 text-gray-700 hover:bg-gray-50 font-semibold"
          >
            View Symptoms
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
