# prompt-guard
PromptGuard is a middleware firewall that sits between user input and any LLM API, analyses every prompt in real-time for injection attacks (jailbreaks, indirect injection, instruction overrides, role hijacking), classifies the attack type and severity, and either blocks, sanitises, or flags the input before it ever reaches the model. 
