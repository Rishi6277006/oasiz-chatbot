import os; print('OPENAI_API_KEY:', os.getenv('OPENAI_API_KEY', 'NOT_FOUND')[:10] + '...' if os.getenv('OPENAI_API_KEY') else 'NOT_FOUND')
