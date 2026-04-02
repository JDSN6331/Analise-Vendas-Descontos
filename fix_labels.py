"""Remove the broken separate script block and add resize logic properly."""
f = open('analytics/dashboard/generator.py', 'r', encoding='utf-8')
c = f.read()
f.close()

# 1. Remove the broken separate script block
broken_script = """
    <script>
    // Debounced resize handler for screen changes (monitor <-> notebook)
    (function() {
        var resizeTimer = null;
        window.addEventListener('resize', function() {
            clearTimeout(resizeTimer);
            resizeTimer = setTimeout(function() {
                if (typeof resizeAllCharts === 'function') {
                    requestAnimationFrame(resizeAllCharts);
                }
            }, 200);
        });
    })();
    </script>
"""
assert broken_script in c, "Could not find broken script to remove"
c = c.replace(broken_script, '\n')
print("1. Removed broken script block")

# 2. Add debounced resize INSIDE the f-string, using proper {{ }} escaping
# Find the resizeAllCharts closing and add debounced listener after it
old_resize_end = """        function resizeAllCharts() {{
            if (chartEvolucao) chartEvolucao.resize();
            if (chartABC) chartABC.resize();
            if (chartDiaMes) chartDiaMes.resize();
            if (chartSegmentos) chartSegmentos.resize();
            if (chartDiaSemana) chartDiaSemana.resize();
            
            if (typeof chartAlcadaPedidos !== 'undefined' && chartAlcadaPedidos) chartAlcadaPedidos.resize();
            if (typeof chartAlcadaValor !== 'undefined' && chartAlcadaValor) chartAlcadaValor.resize();
            if (motivosChart) motivosChart.resize();
            if (grupoChart) grupoChart.resize();
        }}"""

new_resize_end = """        function resizeAllCharts() {{
            if (chartEvolucao) chartEvolucao.resize();
            if (chartABC) chartABC.resize();
            if (chartDiaMes) chartDiaMes.resize();
            if (chartSegmentos) chartSegmentos.resize();
            if (chartDiaSemana) chartDiaSemana.resize();
            
            if (typeof chartAlcadaPedidos !== 'undefined' && chartAlcadaPedidos) chartAlcadaPedidos.resize();
            if (typeof chartAlcadaValor !== 'undefined' && chartAlcadaValor) chartAlcadaValor.resize();
            if (motivosChart) motivosChart.resize();
            if (grupoChart) grupoChart.resize();
        }}

        // Debounced resize para mudança monitor <-> notebook
        (function() {{
            let resizeTimer = null;
            window.addEventListener('resize', function() {{
                clearTimeout(resizeTimer);
                resizeTimer = setTimeout(function() {{
                    requestAnimationFrame(resizeAllCharts);
                }}, 200);
            }});
        }})();"""

assert old_resize_end in c, "Could not find resizeAllCharts to update"
c = c.replace(old_resize_end, new_resize_end)
print("2. Added debounced resize with proper f-string escaping")

# Write back
f = open('analytics/dashboard/generator.py', 'w', encoding='utf-8')
f.write(c)
f.close()
print("Done!")
