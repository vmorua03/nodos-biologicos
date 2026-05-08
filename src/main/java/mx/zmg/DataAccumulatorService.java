package mx.zmg;

import java.time.LocalDate;
import java.util.*;

public class DataAccumulatorService {

    private final EBirdAPIClient apiClient;
    private final ETLService etlService;

    public DataAccumulatorService(EBirdAPIClient api, ETLService etl) {
        this.apiClient  = api;
        this.etlService = etl;
    }

    public void acumularDatos() throws Exception {
        Set<String> claves = new HashSet<>();
        List<Avistamiento> todos = new ArrayList<>();

        // Bloque A: últimos 30 días en Jalisco
        System.out.println("📡 Fetching observaciones recientes MX-JAL...");
        agregarSinDuplicados(apiClient.fetchRecientes(30), todos, claves);

        // Bloque B: radio 50km desde el centro de GDL
        System.out.println("📡 Fetching radio 50km desde Guadalajara...");
        agregarSinDuplicados(apiClient.fetchPorRadio(20.6597, -103.3496, 50), todos, claves);

        // Bloque C: fechas históricas (temporadas migratorias)
        LocalDate[] fechas = {
            LocalDate.of(2024, 11, 1),
            LocalDate.of(2024, 12, 15),
            LocalDate.of(2025, 2,  1),
            LocalDate.of(2025, 4, 15),
            LocalDate.of(2025, 9, 20),
        };

        for (LocalDate fecha : fechas) {
            System.out.println("📡 Fetching histórico: " + fecha);
            agregarSinDuplicados(apiClient.fetchHistorico(fecha), todos, claves);
            Thread.sleep(350); // Respeta el rate limit de eBird
        }

        System.out.printf("✅ Total registros únicos: %d%n", todos.size());
        etlService.cargar(todos);
    }

    private void agregarSinDuplicados(List<Avistamiento> nuevos,
                                       List<Avistamiento> acumulados,
                                       Set<String> claves) {
        for (Avistamiento a : nuevos) {
            String clave = a.getNombreCientifico() + "|"
                         + a.getLatitud() + "|"
                         + a.getLongitud() + "|"
                         + a.getFecha();
            if (claves.add(clave)) acumulados.add(a);
        }
    }
}