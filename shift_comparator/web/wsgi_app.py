"""
Application WSGI pour déploiement sur Render, Heroku, etc.
Compatible avec Gunicorn.
"""
import json
import os
from datetime import datetime
from urllib.parse import parse_qs, urlparse

from ..models import ShiftType, WorkDay, Scenario
from ..core import ShiftCalculator, ScenarioComparator


class WSGIApplication:
    """Application WSGI pour le comparateur de shifts"""

    def __init__(self):
        self.calculator = ShiftCalculator()
        self.comparator = ScenarioComparator(self.calculator)
        self.scenarios = []

        # Chemin vers les fichiers statiques
        self.static_dir = os.path.join(os.path.dirname(__file__), 'static')

    def __call__(self, environ, start_response):
        """Point d'entrée WSGI"""
        path = environ.get('PATH_INFO', '/')
        method = environ.get('REQUEST_METHOD', 'GET')

        # Router les requêtes
        if method == 'GET':
            if path == '/' or path == '/index.html':
                return self.serve_file('index.html', start_response)
            elif path == '/style.css':
                return self.serve_file('style.css', start_response, 'text/css')
            elif path == '/app.js':
                return self.serve_file('app.js', start_response, 'application/javascript')
            elif path == '/api/scenarios':
                return self.get_scenarios(environ, start_response)
            else:
                return self.not_found(start_response)

        elif method == 'POST':
            if path == '/api/calculate':
                return self.calculate(environ, start_response)
            elif path == '/api/save':
                return self.save(environ, start_response)
            elif path == '/api/compare':
                return self.compare(environ, start_response)
            elif path == '/api/delete':
                return self.delete(environ, start_response)
            else:
                return self.not_found(start_response)

        return self.not_found(start_response)

    def serve_file(self, filename, start_response, content_type='text/html'):
        """Sert un fichier statique"""
        filepath = os.path.join(self.static_dir, filename)

        try:
            with open(filepath, 'rb') as f:
                content = f.read()

            start_response('200 OK', [
                ('Content-Type', f'{content_type}; charset=utf-8'),
                ('Content-Length', str(len(content)))
            ])
            return [content]
        except FileNotFoundError:
            return self.not_found(start_response)

    def get_scenarios(self, environ, start_response):
        """GET /api/scenarios"""
        response = {
            'scenarios': [
                {
                    'id': i,
                    'name': s.name,
                    'days': len(s.work_days),
                    'hourly_rate': s.hourly_rate
                }
                for i, s in enumerate(self.scenarios)
            ]
        }
        return self.json_response(response, start_response)

    def calculate(self, environ, start_response):
        """POST /api/calculate"""
        try:
            data = self.get_json_body(environ)

            name = data.get('name', 'Scénario')
            hourly_rate = float(data.get('hourly_rate', 20.0))
            shifts = data.get('shifts', [])

            if not shifts:
                return self.json_response({'error': 'Aucun shift fourni'}, start_response, '400 Bad Request')

            # Créer les WorkDay
            work_days = []
            for shift in shifts:
                date = datetime.strptime(shift['date'], '%Y-%m-%d')
                shift_type = ShiftType[shift['type']]
                work_days.append(WorkDay(date, shift_type))

            # Calculer
            scenario = Scenario(name, work_days, hourly_rate)
            result = self.calculator.calculate_scenario(scenario)

            # Formater pour JSON
            response = {
                'name': result.scenario_name,
                'hourly_rate': result.hourly_rate,
                'total_hours': result.get_total_hours(),
                'total_pay': result.total_pay,
                'total_bonus': result.total_bonus,
                'breakdown': {
                    'normal': result.total_breakdown.normal_hours,
                    'night': result.total_breakdown.night_hours,
                    'sunday': result.total_breakdown.sunday_hours,
                    'night_sunday': result.total_breakdown.night_sunday_hours
                },
                'days': [
                    {
                        'date': dr.work_day.date.strftime('%Y-%m-%d'),
                        'day_name': dr.work_day.date.strftime('%A'),
                        'shift_type': dr.work_day.shift_type.value,
                        'hours': dr.breakdown.get_total_hours(),
                        'pay': dr.total_pay,
                        'bonus': dr.bonus_pay
                    }
                    for dr in result.day_results
                ]
            }

            return self.json_response(response, start_response)

        except Exception as e:
            return self.json_response({'error': str(e)}, start_response, '500 Internal Server Error')

    def save(self, environ, start_response):
        """POST /api/save"""
        try:
            data = self.get_json_body(environ)

            name = data.get('name', 'Scénario')
            hourly_rate = float(data.get('hourly_rate', 20.0))
            shifts = data.get('shifts', [])

            if not shifts:
                return self.json_response({'error': 'Aucun shift fourni'}, start_response, '400 Bad Request')

            # Créer les WorkDay
            work_days = []
            for shift in shifts:
                date = datetime.strptime(shift['date'], '%Y-%m-%d')
                shift_type = ShiftType[shift['type']]
                work_days.append(WorkDay(date, shift_type))

            # Sauvegarder
            scenario = Scenario(name, work_days, hourly_rate)
            self.scenarios.append(scenario)

            return self.json_response({
                'success': True,
                'message': f"Scénario '{name}' sauvegardé",
                'id': len(self.scenarios) - 1
            }, start_response)

        except Exception as e:
            return self.json_response({'error': str(e)}, start_response, '500 Internal Server Error')

    def compare(self, environ, start_response):
        """POST /api/compare"""
        try:
            data = self.get_json_body(environ)
            scenario_ids = data.get('scenario_ids', [])

            if len(scenario_ids) < 2:
                return self.json_response(
                    {'error': 'Au moins 2 scénarios sont nécessaires'},
                    start_response,
                    '400 Bad Request'
                )

            # Récupérer les scénarios
            scenarios = [self.scenarios[i] for i in scenario_ids if i < len(self.scenarios)]

            if len(scenarios) < 2:
                return self.json_response({'error': 'Scénarios invalides'}, start_response, '400 Bad Request')

            # Comparer
            comparison = self.comparator.compare_scenarios(scenarios)

            # Formater pour JSON
            response = {
                'best': {
                    'name': comparison.best_scenario.scenario_name,
                    'total_pay': comparison.best_scenario.total_pay,
                    'total_hours': comparison.best_scenario.get_total_hours(),
                    'total_bonus': comparison.best_scenario.total_bonus
                },
                'ranking': [
                    {
                        'rank': rank,
                        'name': result.scenario_name,
                        'hours': result.get_total_hours(),
                        'pay': result.total_pay,
                        'bonus': result.total_bonus,
                        'difference': comparison.get_difference_from_best(result),
                        'percentage': comparison.get_percentage_from_best(result)
                    }
                    for rank, result in comparison.get_ranking()
                ]
            }

            return self.json_response(response, start_response)

        except Exception as e:
            return self.json_response({'error': str(e)}, start_response, '500 Internal Server Error')

    def delete(self, environ, start_response):
        """POST /api/delete"""
        try:
            data = self.get_json_body(environ)
            scenario_ids = sorted(data.get('scenario_ids', []), reverse=True)

            for i in scenario_ids:
                if 0 <= i < len(self.scenarios):
                    del self.scenarios[i]

            return self.json_response({
                'success': True,
                'message': f"{len(scenario_ids)} scénario(s) supprimé(s)"
            }, start_response)

        except Exception as e:
            return self.json_response({'error': str(e)}, start_response, '500 Internal Server Error')

    def get_json_body(self, environ):
        """Récupère et parse le body JSON"""
        try:
            content_length = int(environ.get('CONTENT_LENGTH', 0))
        except ValueError:
            content_length = 0

        if content_length > 0:
            body = environ['wsgi.input'].read(content_length).decode('utf-8')
            return json.loads(body)
        return {}

    def json_response(self, data, start_response, status='200 OK'):
        """Envoie une réponse JSON"""
        response = json.dumps(data, ensure_ascii=False, indent=2).encode('utf-8')
        start_response(status, [
            ('Content-Type', 'application/json; charset=utf-8'),
            ('Content-Length', str(len(response)))
        ])
        return [response]

    def not_found(self, start_response):
        """Réponse 404"""
        response = b'Not Found'
        start_response('404 Not Found', [
            ('Content-Type', 'text/plain'),
            ('Content-Length', str(len(response)))
        ])
        return [response]


# Instance globale pour WSGI
application = WSGIApplication()

# Alias pour compatibilité
app = application
