package mx.zmg;

import java.sql.*;

public class Main {
    public static void main(String[] args) throws Exception {

        // Verificar variables de entorno
        String apiKey  = System.getenv("EBIRD_API_KEY");
        String dbPass  = System.getenv("DB_PASSWORD");

        if (apiKey == null || apiKey.isBlank()) {
            System.err.println("❌ Falta: export EBIRD_API_KEY=tu_key");
            System.exit(1);
        }
        if (dbPass == null) dbPass = ""; // Si MySQL no tiene contraseña

        String dbUrl = "jdbc:mysql://localhost:3306/biodiversidad_zmg"
                     + "?useSSL=false&serverTimezone=America/Mexico_City";

        System.out.println("🔌 Conectando a MySQL...");

        try (Connection conn = DriverManager.getConnection(dbUrl, "root", dbPass)) {
            System.out.println("✅ Conexión exitosa.");

            EBirdAPIClient    api         = new EBirdAPIClient();
            ETLService        etl         = new ETLService(conn);
            DataAccumulatorService acc    = new DataAccumulatorService(api, etl);

            acc.acumularDatos();

            System.out.println("\n ETL completo. Siguiente paso: correr kmeans_zmg.py");
        }
    }
}