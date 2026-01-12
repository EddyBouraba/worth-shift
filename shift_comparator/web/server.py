"""
Serveur HTTP simple pour l'interface web.
Utilise uniquement la bibliothèque standard Python (pas de dépendance externe).
"""
import json
import os
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import parse_qs, urlparse
from datetime import datetime

from ..models import ShiftType, WorkDay, Scenario
from ..core import ShiftCalculator, ScenarioComparator
from ..utils import ResultFormatter


class ShiftComparatorHandler(BaseHTTPRequestHandler):
    """Gestionnaire de requêtes HTTP pour l'API"""

    calculator = ShiftCalculator()
    comparator = ScenarioComparator(calculator)
    scenarios = []  # Liste des scénarios sauvegardés

    def do_GET(self):
        """Gère les requêtes GET"""
        parsed_path = urlparse(self.path)

        # Page principale
        if parsed_path.path == '/' or parsed_path.path == '/index.html':
            self.serve_file('index.html', 'text/html')

        # CSS
        elif parsed_path.path == '/style.css':
            self.serve_file('style.css', 'text/css')

        # JavaScript
        elif parsed_path.path == '/app.js':
            self.serve_file('app.js', 'application/javascript')

        # API: Liste des scénarios
        elif parsed_path.path == '/api/scenarios':
            self.send_json_response({
                'scenarios': [
                    {
                        'id': i,
                        'name': s.name,
                        'days': len(s.work_days),
                        'hourly_rate': s.hourly_rate
                    }
                    for i, s in enumerate(self.scenarios)
                ]
            })

        else:
            self.send_error(404, "File not found")

    def do_POST(self):
        """Gère les requêtes POST"""
        parsed_path = urlparse(self.path)
        content_length = int(self.headers.get('Content-Length', 0))
        body = self.rfile.read(content_length).decode('utf-8')

        try:
            data = json.loads(body) if body else {}
        except json.JSONDecodeError:
            self.send_error(400, "Invalid JSON")
            return

        # API: Calculer un scénario
        if parsed_path.path == '/api/calculate':
            self.handle_calculate(data)

        # API: Sauvegarder un scénario
        elif parsed_path.path == '/api/save':
            self.handle_save(data)

        # API: Comparer des scénarios
        elif parsed_path.path == '/api/compare':
            self.handle_compare(data)

        # API: Supprimer des scénarios
        elif parsed_path.path == '/api/delete':
            self.handle_delete(data)

        else:
            self.send_error(404, "Endpoint not found")

    def handle_calculate(self, data):
        """Calcule un scénario"""
        try:
            name = data.get('name', 'Scénario')
            hourly_rate = float(data.get('hourly_rate', 20.0))
            shifts = data.get('shifts', [])

            if not shifts:
                self.send_json_response({'error': 'Aucun shift fourni'}, status=400)
                return

            # Créer les WorkDay
            work_days = []
            for shift in shifts:
                date = datetime.strptime(shift['date'], '%Y-%m-%d')
                shift_type = ShiftType[shift['type']]
                work_days.append(WorkDay(date, shift_type))

            # Créer et calculer le scénario
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

            self.send_json_response(response)

        except Exception as e:
            self.send_json_response({'error': str(e)}, status=500)

    def handle_save(self, data):
        """Sauvegarde un scénario"""
        try:
            name = data.get('name', 'Scénario')
            hourly_rate = float(data.get('hourly_rate', 20.0))
            shifts = data.get('shifts', [])

            if not shifts:
                self.send_json_response({'error': 'Aucun shift fourni'}, status=400)
                return

            # Créer les WorkDay
            work_days = []
            for shift in shifts:
                date = datetime.strptime(shift['date'], '%Y-%m-%d')
                shift_type = ShiftType[shift['type']]
                work_days.append(WorkDay(date, shift_type))

            # Créer et sauvegarder le scénario
            scenario = Scenario(name, work_days, hourly_rate)
            self.scenarios.append(scenario)

            self.send_json_response({
                'success': True,
                'message': f"Scénario '{name}' sauvegardé",
                'id': len(self.scenarios) - 1
            })

        except Exception as e:
            self.send_json_response({'error': str(e)}, status=500)

    def handle_compare(self, data):
        """Compare des scénarios"""
        try:
            scenario_ids = data.get('scenario_ids', [])

            if len(scenario_ids) < 2:
                self.send_json_response(
                    {'error': 'Au moins 2 scénarios sont nécessaires'},
                    status=400
                )
                return

            # Récupérer les scénarios
            scenarios = [self.scenarios[i] for i in scenario_ids if i < len(self.scenarios)]

            if len(scenarios) < 2:
                self.send_json_response({'error': 'Scénarios invalides'}, status=400)
                return

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

            self.send_json_response(response)

        except Exception as e:
            self.send_json_response({'error': str(e)}, status=500)

    def handle_delete(self, data):
        """Supprime des scénarios"""
        try:
            scenario_ids = sorted(data.get('scenario_ids', []), reverse=True)

            for i in scenario_ids:
                if 0 <= i < len(self.scenarios):
                    del self.scenarios[i]

            self.send_json_response({
                'success': True,
                'message': f"{len(scenario_ids)} scénario(s) supprimé(s)"
            })

        except Exception as e:
            self.send_json_response({'error': str(e)}, status=500)

    def serve_file(self, filename, content_type):
        """Sert un fichier statique"""
        web_dir = os.path.dirname(os.path.abspath(__file__))
        filepath = os.path.join(web_dir, 'static', filename)

        try:
            with open(filepath, 'rb') as f:
                content = f.read()
            self.send_response(200)
            self.send_header('Content-Type', content_type)
            self.send_header('Content-Length', len(content))
            self.end_headers()
            self.wfile.write(content)
        except FileNotFoundError:
            self.send_error(404, f"File not found: {filename}")

    def send_json_response(self, data, status=200):
        """Envoie une réponse JSON"""
        response = json.dumps(data, ensure_ascii=False, indent=2)
        self.send_response(status)
        self.send_header('Content-Type', 'application/json; charset=utf-8')
        self.send_header('Content-Length', len(response.encode('utf-8')))
        self.end_headers()
        self.wfile.write(response.encode('utf-8'))

    def log_message(self, format, *args):
        """Override pour un log plus propre"""
        print(f"[{self.log_date_time_string()}] {format % args}")


def run_server(port=8080, host='localhost'):
    """Lance le serveur web"""
    server = HTTPServer((host, port), ShiftComparatorHandler)
    print("=" * 80)
    print("COMPARATEUR DE REMPLACEMENTS 3x8 - Interface Web")
    print("=" * 80)
    print(f"\n✓ Serveur démarré sur http://{host}:{port}")
    print(f"\n📱 Ouvrez votre navigateur à cette adresse: http://{host}:{port}")
    print("\n💡 Pour arrêter le serveur, appuyez sur Ctrl+C\n")
    print("=" * 80)

    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\n\n✓ Serveur arrêté")
        server.shutdown()


if __name__ == "__main__":
    run_server()
