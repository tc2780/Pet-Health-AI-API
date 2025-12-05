import { useNavigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import { Button } from '../components/ui/button';
import { Heart, Stethoscope, PawPrint, TrendingUp, CheckCircle } from 'lucide-react';
import { useEffect } from 'react';

export default function Index() {
  const navigate = useNavigate();
  const { isAuthenticated, isLoading } = useAuth();

  useEffect(() => {
    if (!isLoading && isAuthenticated) {
      navigate('/dashboard');
    }
  }, [isAuthenticated, isLoading, navigate]);

  if (isLoading) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-green-50 via-white to-blue-50">
        <div className="text-center">
          <div className="inline-flex items-center justify-center w-12 h-12 rounded-full bg-green-100 mb-4">
            <Heart className="h-6 w-6 text-green-600 animate-pulse" />
          </div>
          <p className="text-gray-600">Loading...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-green-50 via-white to-blue-50">
      {/* Navigation */}
      <nav className="bg-white border-b border-gray-200 sticky top-0 z-10">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-4 flex items-center justify-between">
          <div className="flex items-center gap-3">
            <div className="bg-gradient-to-br from-green-500 to-green-600 rounded-lg p-2">
              <Heart className="h-6 w-6 text-white fill-white" />
            </div>
            <h1 className="text-2xl font-bold text-gray-900">PetCare</h1>
          </div>

          <div className="flex gap-4">
            <Button
              onClick={() => navigate('/login')}
              variant="outline"
              className="border-gray-200 text-gray-700 hover:bg-gray-50 font-semibold"
            >
              Sign In
            </Button>
            <Button
              onClick={() => navigate('/register')}
              className="bg-gradient-to-r from-green-500 to-green-600 hover:from-green-600 hover:to-green-700 text-white font-semibold"
            >
              Get Started
            </Button>
          </div>
        </div>
      </nav>

      {/* Hero Section */}
      <section className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-24">
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-12 items-center">
          {/* Left Content */}
          <div>
            <h2 className="text-5xl md:text-6xl font-bold text-gray-900 mb-6 leading-tight">
              Keep Your Pet <span className="bg-gradient-to-r from-green-500 to-green-600 bg-clip-text text-transparent">Healthy & Happy</span>
            </h2>
            <p className="text-xl text-gray-600 mb-8 leading-relaxed">
              Track your pet's health symptoms in one place. Get AI-powered health insights to help you make informed decisions about your pet's care.
            </p>

            <div className="flex gap-4">
              <Button
                onClick={() => navigate('/register')}
                className="px-8 h-12 bg-gradient-to-r from-green-500 to-green-600 hover:from-green-600 hover:to-green-700 text-white font-semibold text-lg rounded-lg"
              >
                Start Free
              </Button>
              <Button
                onClick={() => navigate('/login')}
                variant="outline"
                className="px-8 h-12 border-green-200 text-green-600 hover:bg-green-50 font-semibold text-lg"
              >
                Sign In
              </Button>
            </div>
          </div>

          {/* Right Illustration */}
          <div className="relative">
            <div className="!bg-gradient-to-br !from-green-100 !to-blue-100 rounded-3xl p-12 aspect-square flex items-center justify-center">
              <div className="text-center">
                <PawPrint className="h-32 w-32 text-green-500 mx-auto mb-4 opacity-80" />
                <p className="text-gray-600 font-medium">Your Pet's Health, Your Peace of Mind</p>
              </div>
            </div>

            {/* Floating Cards */}
            <div className="absolute -bottom-4 -left-4 bg-white rounded-2xl shadow-xl p-4 border border-gray-100 w-48">
              <div className="flex items-center gap-3 mb-2">
                <Heart className="h-5 w-5 text-red-500 fill-red-500" />
                <p className="font-semibold text-gray-900">10K+ Happy Pets</p>
              </div>
              <p className="text-sm text-gray-600">Pet owners trust us</p>
            </div>

            <div className="absolute -top-4 -right-4 bg-white rounded-2xl shadow-xl p-4 border border-gray-100 w-48">
              <div className="flex items-center gap-3 mb-2">
                <Stethoscope className="h-5 w-5 text-green-500" />
                <p className="font-semibold text-gray-900">AI Advisor</p>
              </div>
              <p className="text-sm text-gray-600">24/7 health insights</p>
            </div>
          </div>
        </div>
      </section>

      {/* Features Section */}
      <section className="bg-white py-24">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center mb-16">
            <h3 className="text-4xl font-bold text-gray-900 mb-4">Why Choose PetCare?</h3>
            <p className="text-xl text-gray-600 max-w-2xl mx-auto">
              Everything you need to monitor and improve your pet's health
            </p>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8">
            {/* Feature 1 */}
            <div className="bg-gradient-to-br from-green-50 to-blue-50 rounded-2xl p-8 border border-green-100">
              <div className="w-12 h-12 bg-green-500 rounded-lg flex items-center justify-center mb-4">
                <PawPrint className="h-6 w-6 text-white" />
              </div>
              <h4 className="text-xl font-bold text-gray-900 mb-3">Multi-Pet Support</h4>
              <p className="text-gray-600">
                Manage health records for all your pets in one dashboard
              </p>
            </div>

            {/* Feature 2 */}
            <div className="bg-gradient-to-br from-orange-50 to-red-50 rounded-2xl p-8 border border-orange-100">
              <div className="w-12 h-12 bg-orange-500 rounded-lg flex items-center justify-center mb-4">
                <TrendingUp className="h-6 w-6 text-white" />
              </div>
              <h4 className="text-xl font-bold text-gray-900 mb-3">Track Symptoms</h4>
              <p className="text-gray-600">
                Log symptoms with severity levels and detailed notes
              </p>
            </div>

            {/* Feature 3 */}
            <div className="bg-gradient-to-br from-purple-50 to-pink-50 rounded-2xl p-8 border border-purple-100">
              <div className="w-12 h-12 bg-purple-500 rounded-lg flex items-center justify-center mb-4">
                <Stethoscope className="h-6 w-6 text-white" />
              </div>
              <h4 className="text-xl font-bold text-gray-900 mb-3">AI Health Advisor</h4>
              <p className="text-gray-600">
                Get AI-powered insights about your pet's symptoms
              </p>
            </div>

            {/* Feature 4 */}
            <div className="bg-gradient-to-br from-blue-50 to-cyan-50 rounded-2xl p-8 border border-blue-100">
              <div className="w-12 h-12 bg-blue-500 rounded-lg flex items-center justify-center mb-4">
                <CheckCircle className="h-6 w-6 text-white" />
              </div>
              <h4 className="text-xl font-bold text-gray-900 mb-3">Always Available</h4>
              <p className="text-gray-600">
                Access your pet's health records anytime, anywhere
              </p>
            </div>

            {/* Feature 5 */}
            <div className="!bg-gradient-to-br !from-pink-50 !to-rose-50 rounded-2xl p-8 border border-pink-100">
              <div className="w-12 h-12 bg-pink-500 rounded-lg flex items-center justify-center mb-4">
                <Heart className="h-6 w-6 text-white fill-white" />
              </div>
              <h4 className="text-xl font-bold text-gray-900 mb-3">Secure & Private</h4>
              <p className="text-gray-600">
                Your pet's health data is encrypted and secure
              </p>
            </div>

            {/* Feature 6 */}
            <div className="bg-gradient-to-br from-indigo-50 to-blue-50 rounded-2xl p-8 border border-indigo-100">
              <div className="w-12 h-12 bg-indigo-500 rounded-lg flex items-center justify-center mb-4">
                <TrendingUp className="h-6 w-6 text-white" />
              </div>
              <h4 className="text-xl font-bold text-gray-900 mb-3">Health Trends</h4>
              <p className="text-gray-600">
                Identify patterns to catch health issues early
              </p>
            </div>
          </div>
        </div>
      </section>

      {/* CTA Section */}
      <section className="py-24">
        <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 text-center">
          <div className="bg-gradient-to-r from-green-500 to-green-600 rounded-3xl p-12 text-white">
            <h3 className="text-4xl font-bold mb-4">Ready to Care Better?</h3>
            <p className="text-xl text-green-100 mb-8 max-w-2xl mx-auto">
              Join thousands of pet owners who trust PetCare with their pet's health
            </p>
            <Button
              onClick={() => navigate('/register')}
              className="px-8 h-12 bg-white hover:bg-gray-100 text-green-600 font-semibold text-lg rounded-lg"
            >
              Start Your Free Account
            </Button>
          </div>
        </div>
      </section>

      {/* Footer */}
      <footer className="border-t border-gray-200 bg-white py-12">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 text-center text-gray-600">
          <p className="mb-2">© 2024 PetCare. All rights reserved.</p>
          <p className="text-sm">Taking care of your pet, every step of the way.</p>
        </div>
      </footer>
    </div>
  );
}
