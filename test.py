from requests import get, post, delete

# first pack of tests
print(get('http://localhost:5000/api/translate/Семья').json())
print(get('http://localhost:5000/api/translate/Семья&rrr@222.ru').json())
print(get('http://localhost:5000/api/translate/Семья&zero').json())
print(get('http://localhost:5000/api/translate/Семья&').json())
print(get('http://localhost:5000/api/translate/&rrr@222.ru').json())
print(get('http://localhost:5000/api/translate/&').json())
print(get('http://localhost:5000/api/translate/').json())
print('\n')


# second pack of tests
print(get('http://localhost:5000/api/show_history/rrr@222.ru').json())
print(get('http://localhost:5000/api/show_history/rrr@222.ru&').json())
print(get('http://localhost:5000/api/show_history/rrr@222.ru&hello').json())
print(get('http://localhost:5000/api/show_history/rrr@222.ru&rrr').json())
print(get('http://localhost:5000/api/show_history/rr22.ru&rrr').json())
print(get('http://localhost:5000/api/show_history/&rrr').json())
print(get('http://localhost:5000/api/show_history/&').json())
print(get('http://localhost:5000/api/show_history/').json())
print('\n')

# third pack of tests
print(get('http://localhost:5000/api/about/').json())