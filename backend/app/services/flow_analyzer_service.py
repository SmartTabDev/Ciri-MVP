import json
from typing import Dict, Any, List, Optional
from app.services.ai_service import SimpleAIService

class FlowAnalyzerService:
    def __init__(self):
        self.ai_service = SimpleAIService()
    
    def analyze_flow_builder_data(self, flow_data: Dict[str, Any]) -> str:
        """Analyze flow builder data and generate text instructions using AI."""
        try:
            nodes = flow_data.get('nodes', [])
            edges = flow_data.get('edges', [])
            
            if not nodes:
                return "No flow structure found."
            
            flow_description = self._create_flow_description(nodes, edges)
            print("flow_description===========>", flow_description)
            prompt = self._create_analysis_prompt(flow_description)
            print("prompt===========>", prompt)
            
            # Use asyncio to run the async method
            import asyncio
            response = asyncio.run(self.ai_service.generate_free_text(prompt))
            
            return response.strip()
            
        except Exception as e:
            print(f"Error analyzing flow data: {e}")
            return "Unable to analyze flow structure."
    
    def _create_flow_description(self, nodes: List[Dict], edges: List[Dict]) -> str:
        """Create a human-readable description of the flow structure."""
        description = "Flow Structure:\n\n"
        
        # Describe nodes
        description += "Nodes:\n"
        for node in nodes:
            node_type = node.get('type', 'unknown')
            node_id = node.get('id', 'unknown')
            
            if node_type == 'start':
                description += f"- Start Node ({node_id}): Beginning of the conversation flow\n"
            elif node_type == 'end':
                description += f"- End Node ({node_id}): End of the conversation flow\n"
            elif node_type == 'text-message':
                message = node.get('data', {}).get('message', 'No message')
                channel = node.get('data', {}).get('channel', 'unknown')
                description += f"- Text Message Node ({node_id}): Send '{message}' via {channel}\n"
            elif node_type == 'conditional-path':
                condition = node.get('data', {}).get('condition', {})
                paths = node.get('data', {}).get('paths', [])
                condition_label = condition.get('label', 'No condition') if condition else 'No condition'
                description += f"- Conditional Node ({node_id}): {condition_label} with {len(paths)} paths\n"
                for path in paths:
                    description += f"  * Path: {path.get('value', 'Unknown path')}\n"
        
        # Describe connections
        description += "\nConnections:\n"
        for edge in edges:
            source = edge.get('source', 'unknown')
            target = edge.get('target', 'unknown')
            description += f"- {source} → {target}\n"
        
        return description
    
    def _create_analysis_prompt(self, flow_description: str) -> str:
        """Create a prompt for AI analysis of the flow."""
        return f"""
        You are an AI assistant that analyzes conversation flow structures and generates clear, actionable text instructions for customer service representatives.

        Please analyze the following conversation flow structure and provide:

        1. **Flow Overview**: A brief summary of what this conversation flow accomplishes
        2. **Key Instructions**: Step-by-step instructions for handling customer interactions
        3. **Decision Points**: When and how to make decisions based on customer responses
        4. **Best Practices**: Recommendations for effective communication

        Flow Structure:
        {flow_description}

        Please provide just clear, concise instructions that a customer service representative can follow easily. Focus on practical, actionable guidance.
        """
    
    def update_flow_context(self, company_id: int, flow_builder_data: str) -> Optional[str]:
        """Update the flow_context with AI-generated instructions based on flow_builder_data."""
        try:
            flow_data = json.loads(flow_builder_data)
            flow_context = self.analyze_flow_builder_data(flow_data)
            print("flow_context===========>", flow_context)
            return flow_context
            
        except json.JSONDecodeError:
            print("Invalid JSON in flow_builder_data")
            return None
        except Exception as e:
            print(f"Error updating flow context: {e}")
            return None 