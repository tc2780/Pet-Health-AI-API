import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { EndpointDemo } from "@/components/EndpointDemo";

export default function Index() {
  const base_url = "http://localhost:8000";
  const tabEndpoints = [
    {
      tabName: "General",
      tabValue: "general",
      subEndpoints: [
        {
          title: "Root/Welcome Endpoint",
          description: "Get data from sub-endpoint 1A",
          endpoint: `${base_url}/`,
          method: "GET",
        },
        {
          title: "Health Check",
          description: "Get data from sub-endpoint 1B",
          endpoint: `${base_url}/health`,
          method: "GET",
        },
      ],
    },
    {
      tabName: "Authentication",
      tabValue: "authentication",
      subEndpoints: [
        {
          title: "Register new user",
          description: "Get data from sub-endpoint 1A",
          endpoint: `${base_url}/api/v1/auth/register`,
          method: "POST",
        },
        {
          title: "Login (returns JWT token)",
          description: "Get data from sub-endpoint 1B",
          endpoint: `${base_url}/api/v1/auth/login`,
          method: "POST",
        },
        {
          title: "Get current user info",
          description: "Get data from sub-endpoint 1C",
          endpoint: `${base_url}/api/v1/auth/me`,
          method: "GET",
        },
      ],
    },
    {
      tabName: "Users",
      tabValue: "users",
      subEndpoints: [
        {
          title: "Get current user profile",
          description: "Get data from sub-endpoint 2A",
          endpoint: `${base_url}/api/v1/users/me`,
          method: "GET",
        },
        {
          title: "Update current user profile",
          description: "Get data from sub-endpoint 2B",
          endpoint: `${base_url}/api/v1/users/me`,
          method: "PUT",
        },
        {
          title: "Delete user account",
          description: "Get data from sub-endpoint 2C",
          endpoint: `${base_url}/api/v1/users/me`,
          method: "DELETE",
        },
        {
          title: "Export all user data",
          description: "Get data from sub-endpoint 2D",
          endpoint: `${base_url}/api/v1/users/export`,
          method: "GET",
        },
      ],
    },
    {
      tabName: "Pets",
      tabValue: "pets",
      subEndpoints: [
        {
          title: "Create new pet",
          description: "Get data from sub-endpoint 3A",
          endpoint: `${base_url}/api/v1/pets/`,
          method: "POST",
        },
        {
          title: "Get all user's pets",
          description: "Get data from sub-endpoint 3B",
          endpoint: `${base_url}/api/v1/pets/`,
          method: "GET",
        },
        {
          title: "Get specific pet with symptoms",
          description: "Get data from sub-endpoint 3C",
          endpoint: `${base_url}/api/v1/pets/{pet_id}`,
          method: "GET",
        },
        {
          title: "Update pet information",
          description: "Get data from sub-endpoint 3D",
          endpoint: `${base_url}/api/v1/pets/{pet_id}`,
          method: "PUT",
        },
        {
          title: "Delete pet",
          description: "Get data from sub-endpoint 3D",
          endpoint: `${base_url}/api/v1/pets/{pet_id}`,
          method: "DELETE",
        },
        {
          title: "Sync single pet with vet service",
          description: "Get data from sub-endpoint 3D",
          endpoint: `${base_url}/api/v1/pets/{pet_id}/sync`,
          method: "POST",
        },
        {
          title: "Sync all user's pets with vet service",
          description: "Get data from sub-endpoint 3D",
          endpoint: `${base_url}/api/v1/pets/sync-all`,
          method: "POST",
        },
      ],
    },
    {
      tabName: "Symptoms - CRUD",
      tabValue: "symptoms-crud",
      subEndpoints: [
        {
          title: "Create new symptom",
          description: "Get data from sub-endpoint 4A",
          endpoint: `${base_url}/api/v1/symptoms/`,
          method: "POST",
        },
        {
          title: "Get symptoms for specific pet",
          description: "Get data from sub-endpoint 4B",
          endpoint: `${base_url}/api/v1/symptoms/pet/{pet_id}`,
          method: "GET",
        },
        {
          title: "Get symptoms for all user's pets",
          description: "Get data from sub-endpoint 4C",
          endpoint: `${base_url}/api/v1/symptoms/my-pets`,
          method: "GET",
        },
        {
          title: "Get specific symptom",
          description: "Get data from sub-endpoint 4D",
          endpoint: `${base_url}/api/v1/symptoms/{symptom_id}`,
          method: "GET",
        },
        {
          title: "Update symptom",
          description: "Get data from sub-endpoint 4D",
          endpoint: `${base_url}/api/v1/symptoms/{symptom_id}`,
          method: "PUT",
        },
        {
          title: "Delete symptom",
          description: "Get data from sub-endpoint 4D",
          endpoint: `${base_url}/api/v1/symptoms/{symptom_id}`,
          method: "DELETE",
        },
      ],
    },
    {
      tabName: "Symptoms - AI Assessment",
      tabValue: "symptoms-ai-assessment",
      subEndpoints: [
        {
          title: "Create AI assessment for symptoms",
          description: "Get data from sub-endpoint 4A",
          endpoint: `${base_url}/api/v1/symptoms/assess`,
          method: "POST",
        },
        {
          title: "Get assessments for specific pet",
          description: "Get data from sub-endpoint 4B",
          endpoint: `${base_url}/api/v1/symptoms/assessments/pet/{pet_id}`,
          method: "GET",
        },
        {
          title: "Get assessments for all user's pets",
          description: "Get data from sub-endpoint 4C",
          endpoint: `${base_url}/api/v1/symptoms/assessments/my-pets`,
          method: "GET",
        },
        {
          title: "Get specific assessment",
          description: "Get data from sub-endpoint 4D",
          endpoint: `${base_url}/api/v1/symptoms/assessments/{assessment_id}`,
          method: "GET",
        },
      ],
    },
  ];

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-50 to-slate-100">
      <div className="container max-w-6xl mx-auto px-4 py-12">
        <div className="mb-12">
          <h1 className="text-4xl font-bold text-slate-900 mb-3">
            Endpoint Demo
          </h1>
          <p className="text-lg text-slate-600 max-w-2xl">
            Test and demo API endpoints. Select a tab to view the endpoints for those sections
            and call them to see their responses.
          </p>
        </div>

        <Tabs defaultValue="general" className="w-full">
          <TabsList className="flex flex-wrap gap-2 mb-8 h-auto bg-transparent p-0">
            {tabEndpoints.map((tab) => (
              <TabsTrigger key={tab.tabValue} value={tab.tabValue}>
                {tab.tabName}
              </TabsTrigger>
            ))}
          </TabsList>

          {tabEndpoints.map((tab) => (
            <TabsContent
              key={tab.tabValue}
              value={tab.tabValue}
              className="space-y-8"
            >
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-2 gap-6">
                {tab.subEndpoints.map((subEndpoint, idx) => (
                  <EndpointDemo
                    key={idx}
                    title={subEndpoint.title}
                    description={subEndpoint.description}
                    endpoint={subEndpoint.endpoint}
                    method={subEndpoint.method}
                  />
                ))}
              </div>
            </TabsContent>
          ))}
        </Tabs>
      </div>
    </div>
  );
}
