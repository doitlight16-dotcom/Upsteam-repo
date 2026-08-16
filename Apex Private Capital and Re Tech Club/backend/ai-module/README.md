# ai-module (placeholder)

Stand-in service implementing the contract `AIModulePort` will call from
the backend. Swap this out for the real implementation (LLM API wrapper or
custom model service) once that decision is made -- the backend should not
need to change, only this service and its Dockerfile.
