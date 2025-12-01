# ADR-002: Use Local LLM (Ollama) for AI Processing

## Status
Accepted

## Date
2025-11-30

## Context
We need to choose an AI solution for veterinary symptom analysis. Key requirements:
- Process sensitive pet health data privately
- Provide consistent, reliable AI responses
- Control costs for API usage
- Ensure system works without internet dependencies

## Decision
We will use Ollama with local LLMs (Llama 2/3) as our primary AI solution, with optional OpenAI integration for enhanced features.

## Rationale
**Pros:**
- **Privacy**: Pet health data never leaves our infrastructure
- **Cost Control**: No per-request API fees after initial setup
- **Reliability**: No external API dependencies or rate limits
- **Compliance**: Easier GDPR/HIPAA compliance with local processing
- **Performance**: No network latency for AI requests
- **Customization**: Ability to fine-tune models for veterinary use cases

**Cons:**
- **Hardware Requirements**: Requires significant RAM/CPU resources
- **Setup Complexity**: More complex deployment than API calls
- **Model Quality**: May not match GPT-4 quality initially
- **Maintenance**: Need to manage model updates and optimization

**Alternatives Considered:**
- **OpenAI API**: Excellent quality but privacy concerns and ongoing costs
- **Anthropic Claude**: Similar issues to OpenAI
- **Google Gemini**: Good free tier but still external dependency
- **Hugging Face**: Good option but less optimized than Ollama

## Consequences
- **Positive**: Complete control over pet health data privacy
- **Positive**: Predictable infrastructure costs
- **Positive**: System works offline/in air-gapped environments
- **Negative**: Higher infrastructure requirements for deployment
- **Negative**: Need expertise in LLM deployment and optimization
- **Negative**: May need fallback to cloud APIs for complex cases

## Implementation Strategy
1. **Phase 1**: Deploy Ollama with Llama 2 7B model for basic functionality
2. **Phase 2**: Optimize prompts and potentially fine-tune for veterinary domain
3. **Phase 3**: Add hybrid approach with cloud APIs for complex cases
4. **Monitoring**: Track AI response quality and adjust models as needed

## Technical Requirements
- **Development**: 16GB RAM minimum, GPU recommended
- **Production**: Dedicated AI servers with 32GB+ RAM
- **Fallback**: Optional OpenAI integration for edge cases
- **Caching**: Redis caching for common symptom patterns