import os
import sys
import time
from Board import Board
from Knight import Knight
from KnightTourSolver import KnightTourSolver

def clear_screen():
    """Efface le contenu de la console."""
    os.system('cls' if os.name == 'nt' else 'clear')

def extract_path_from_board(board):
    """Extract the solution path from the board grid."""
    path = []
    for move_number in range(64):
        for i in range(board.size):
            for j in range(board.size):
                if board.grid[i][j] == move_number:
                    path.append((i, j))
                    break
    return path

def format_results(algorithm_name, success, stats, elapsed_time):
    """Format and display algorithm results."""
    print(f"\n{'='*60}")
    print(f"  {algorithm_name}")
    print(f"{'='*60}")
    print(f"  Résultat:           {'✓ SUCCÈS' if success else '✗ ÉCHOUÉ'}")
    print(f"  Temps:              {elapsed_time:.2f} secondes")
    print(f"  Étapes:             {stats.get('steps', 0)}")
    print(f"  Retours en arrière: {stats.get('backtracks', 0)}")
    print(f"{'='*60}\n")

def run_algorithm_comparison():
    """Run both algorithms and compare their performance."""
    clear_screen()
    print("\n" + "="*60)
    print("  COMPARAISON DES ALGORITHMES - KNIGHT'S TOUR CSP")
    print("="*60)
    
    results = {}
    
    # Algorithm 1: Basic Backtracking
    print("\n⏳ Exécution de l'algorithme classique...")
    board_basic = Board(8)
    knight_basic = Knight()
    solver_basic = KnightTourSolver(board_basic, knight_basic)
    solver_basic.reset_stats()
    
    start_time = time.time()
    success_basic = solver_basic.solve_basic(0, 0, 0)
    time_basic = time.time() - start_time
    
    path_basic = extract_path_from_board(board_basic) if success_basic else []
    format_results("1. BACKTRACKING CLASSIQUE", success_basic, solver_basic.stats, time_basic)
    
    results['basic'] = {
        'success': success_basic,
        'path': path_basic,
        'stats': solver_basic.stats.copy(),
        'time': time_basic,
        'board': board_basic
    }
    
    # Algorithm 2: Enhanced with CSP Heuristics
    print("⏳ Exécution de l'algorithme avec heuristiques CSP...")
    board_enhanced = Board(8)
    knight_enhanced = Knight()
    solver_enhanced = KnightTourSolver(board_enhanced, knight_enhanced)
    solver_enhanced.reset_stats()
    
    start_time = time.time()
    success_enhanced = solver_enhanced.solve_enhanced(0, 0, 0)
    time_enhanced = time.time() - start_time
    
    path_enhanced = extract_path_from_board(board_enhanced) if success_enhanced else []
    format_results("2. BACKTRACKING AVEC HEURISTIQUES CSP (MRV + LCV)", success_enhanced, solver_enhanced.stats, time_enhanced)
    
    results['enhanced'] = {
        'success': success_enhanced,
        'path': path_enhanced,
        'stats': solver_enhanced.stats.copy(),
        'time': time_enhanced,
        'board': board_enhanced
    }
    
    # Comparison
    print("\n" + "="*60)
    print("  COMPARAISON FINALE")
    print("="*60)
    
    if success_basic and success_enhanced:
        speedup = results['basic']['time'] / results['enhanced']['time']
        improvement = ((results['basic']['stats']['steps'] - results['enhanced']['stats']['steps']) / 
                      results['basic']['stats']['steps'] * 100)
        
        print(f"  Temps: {results['enhanced']['time']:.2f}s vs {results['basic']['time']:.2f}s")
        print(f"  Accélération: {speedup:.2f}x plus rapide avec heuristiques")
        print(f"  Réduction d'étapes: {improvement:.1f}%")
        print(f"  Réduction de retours: {results['basic']['stats']['backtracks']} vs {results['enhanced']['stats']['backtracks']}")
    else:
        if not success_basic:
            print("  ⚠ L'algorithme classique n'a pas trouvé de solution")
        if not success_enhanced:
            print("  ⚠ L'algorithme avec heuristiques n'a pas trouvé de solution")
    
    print("="*60)
    print("\n✓ Comparaison terminée! Lancement de l'interface graphique...\n")
    
    return results

def main():
    """
    Fonction principale: exécute la comparaison puis lance l'interface graphique.
    """
    try:
        # Run comparison and get results
        comparison_results = run_algorithm_comparison()
        
        # Import and launch GUI with results
        try:
            from interface import KnightTourGame
            game = KnightTourGame()
            # Store the results in the game instance
            game.comparison_results = comparison_results
            game.run()
        except ImportError as e:
            print(f"Erreur d'importation de l'interface: {e}")
            print("Assurez-vous que le fichier 'interface.py' se trouve dans le même répertoire.")
            input("Appuyez sur Entrée pour quitter...")
    
    except Exception as e:
        print(f"Erreur fatale: {e}")
        import traceback
        traceback.print_exc()
        input("Appuyez sur Entrée pour quitter...")

if __name__ == "__main__":
    main()
