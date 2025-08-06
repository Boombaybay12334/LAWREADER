# answer_simplifier.py
from typing import Dict, Any, List, Optional
import re
import textwrap

class AnswerSimplifier:
    def __init__(self):
        """Initialize the answer simplifier with templates and formatting rules."""
        self.templates = {
            'full_answer': """
🏛️ LEGAL GUIDANCE

📝 Your Situation:
{scenario_example}

⚖️ Relevant Legal Principles:
{principles_text}

📋 Constitutional/Legal Articles:
{articles_text}

💡 Summary:
{summary}
            """.strip(),
            
            'no_articles': """
🏛️ LEGAL GUIDANCE

📝 Your Situation:
{scenario_example}

⚖️ Relevant Legal Principles:
{principles_text}

💡 Summary:
{summary}
            """.strip(),
            
            'basic': """
🏛️ LEGAL GUIDANCE

📝 Your Situation:
{scenario_example}

💡 Key Information:
{summary}
            """.strip()
        }
    
    def simplify_answer(self, context: Dict[str, Any]) -> str:
        """
        Convert article + principle + scenario context into plain language output.
        
        Args:
            context: Dictionary from traversal.expand_context()
            
        Returns:
            User-friendly explanation string
        """
        if not context:
            return "❌ No legal context found for your query."
        
        # Extract scenario information
        scenario = context.get('scenario', {})
        scenario_example = scenario.get('example', 'No specific example available')
        
        # Process principles
        principles = context.get('principles', [])
        principles_text = self._format_principles(principles)
        
        # Process articles
        articles = context.get('articles', [])
        articles_text = self._format_articles(articles)
        
        # Generate summary
        summary = self._generate_summary(scenario, principles, articles)
        
        # Choose appropriate template
        if articles_text and principles_text:
            template = self.templates['full_answer']
            return template.format(
                scenario_example=scenario_example,
                principles_text=principles_text,
                articles_text=articles_text,
                summary=summary
            )
        elif principles_text:
            template = self.templates['no_articles']
            return template.format(
                scenario_example=scenario_example,
                principles_text=principles_text,
                summary=summary
            )
        else:
            template = self.templates['basic']
            return template.format(
                scenario_example=scenario_example,
                summary=summary
            )
    
    def _format_principles(self, principles: List[Dict[str, Any]]) -> str:
        """Format principles for display."""
        if not principles:
            return "No specific legal principles found."
        
        formatted_principles = []
        for i, principle in enumerate(principles, 1):
            text = principle.get('text', '').strip()
            if text:
                # Clean up the text
                text = self._clean_text(text)
                formatted_principles.append(f"• {text}")
        
        return '\n'.join(formatted_principles) if formatted_principles else "No principle details available."
    
    def _format_articles(self, articles: List[Dict[str, Any]]) -> str:
        """Format articles for display."""
        if not articles:
            return ""
        
        formatted_articles = []
        for article in articles:
            title = article.get('title', '').strip()
            summary = article.get('description', '').strip()
            number = "Article" + article.get("number",'').strip()
            if title:
                article_text = f"📜{number} {title}"
                if summary:
                    # Clean up the summary text
                    summary = self._clean_text(summary)
                    article_text += f"\n   {summary}"
                formatted_articles.append(article_text)
        
        return '\n\n'.join(formatted_articles) if formatted_articles else ""
    
    def _generate_summary(self, scenario: Dict[str, Any], 
                         principles: List[Dict[str, Any]], 
                         articles: List[Dict[str, Any]]) -> str:
        """Generate a summary based on available context."""
        summary_parts = []
        
        # Count available information
        num_principles = len([p for p in principles if p.get('text', '').strip()])
        num_articles = len([a for a in articles if a.get('title', '').strip()])
        
        if num_principles > 0 and num_articles > 0:
            summary_parts.append(f"Found {num_principles} relevant legal principle(s) and {num_articles} constitutional/legal article(s) that apply to your situation.")
        elif num_principles > 0:
            summary_parts.append(f"Found {num_principles} relevant legal principle(s) that apply to your situation.")
        elif num_articles > 0:
            summary_parts.append(f"Found {num_articles} relevant constitutional/legal article(s) that apply to your situation.")
        
        # Add general advice
        summary_parts.extend([
            "This information is based on Indian legal framework.",
            "For specific legal advice, please consult with a qualified lawyer.",
            "Laws may vary by state and specific circumstances."
        ])
        
        return ' '.join(summary_parts)
    
    def _clean_text(self, text: str) -> str:
        """Clean and format text for better readability."""
        if not text:
            return ""
        
        # Remove excessive whitespace
        text = re.sub(r'\s+', ' ', text.strip())
        
        # Wrap long lines
        if len(text) > 100:
            text = textwrap.fill(text, width=80, subsequent_indent='   ')
        
        return text
    
    def create_short_answer(self, context: Dict[str, Any]) -> str:
        """Create a concise version of the answer."""
        if not context:
            return "No relevant legal information found."
        
        scenario = context.get('scenario', {})
        principles = context.get('principles', [])
        articles = context.get('articles', [])
        
        parts = []
        
        # Add key principle if available
        if principles:
            first_principle = principles[0].get('text', '').strip()
            if first_principle:
                clean_principle = self._clean_text(first_principle)
                if len(clean_principle) > 150:
                    clean_principle = clean_principle[:150] + "..."
                parts.append(f"Key principle: {clean_principle}")
        
        # Add main article if available
        if articles:
            first_article = articles[0]
            title = first_article.get('title', '').strip()
            if title:
                parts.append(f"Relevant law: {title}")
        
        if not parts:
            parts.append("Legal context found in database.")
        
        parts.append("Consult a lawyer for specific advice.")
        
        return ' | '.join(parts)
    
    def format_for_api(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Format the answer for API response."""
        full_answer = self.simplify_answer(context)
        short_answer = self.create_short_answer(context)
        
        return {
            'full_answer': full_answer,
            'short_answer': short_answer,
            'context_summary': {
                'scenario_matched': bool(context.get('scenario', {}).get('example')),
                'principles_count': len(context.get('principles', [])),
                'articles_count': len(context.get('articles', [])),
                'scenario_id': context.get('scenario_id')
            },
            'raw_context': context
        }


# Standalone function for easy LLM code generation
def simplify_answer(context: Dict[str, Any]) -> str:
    """
    Simple interface function to convert context into plain language.
    
    Args:
        context: Dictionary from traversal.expand_context()
        
    Returns:
        User-friendly explanation string
    """
    simplifier = AnswerSimplifier()
    return simplifier.simplify_answer(context)


if __name__ == "__main__":
    # Test the answer simplifier with mock data
    mock_context = {
        'scenario_id': 'test_scenario_1',
        'scenario': {
            'id': 'test_scenario_1',
            'example': 'A person was detained by police during a peaceful protest against government policy',
            'type': 'scenario'
        },
        'principles': [
            {
                'id': 'principle_1',
                'text': 'Citizens have the fundamental right to peaceful assembly and protest',
                'type': 'principle'
            },
            {
                'id': 'principle_2', 
                'text': 'Police detention must be based on reasonable grounds and proper procedures',
                'type': 'principle'
            }
        ],
        'articles': [
            {
                'id': 'article_19',
                'title': 'Article 19 - Right to Freedom of Speech and Expression',
                'layman_summary': 'This article guarantees citizens the right to express their views freely, including through peaceful protests, subject to reasonable restrictions',
                'type': 'article'
            }
        ]
    }
    
    print("Testing Answer Simplifier...")
    print("=" * 60)
    
    simplifier = AnswerSimplifier()
    
    # Test full answer
    print("FULL ANSWER:")
    print(simplifier.simplify_answer(mock_context))
    
    print("\n" + "=" * 60)
    
    # Test short answer
    print("SHORT ANSWER:")
    print(simplifier.create_short_answer(mock_context))
    
    print("\n" + "=" * 60)
    
    # Test API format
    print("API FORMAT:")
    api_response = simplifier.format_for_api(mock_context)
    print(f"Context Summary: {api_response['context_summary']}")
    print(f"Short: {api_response['short_answer']}")
    
    print("\n" + "=" * 60)
    
    # Test with minimal context
    print("MINIMAL CONTEXT TEST:")
    minimal_context = {
        'scenario': {
            'example': 'Basic legal query with no detailed context'
        },
        'principles': [],
        'articles': []
    }
    print(simplifier.simplify_answer(minimal_context))
