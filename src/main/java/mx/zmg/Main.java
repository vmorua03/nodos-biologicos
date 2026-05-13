package mx.zmg;
 
import io.github.cdimascio.dotenv.Dotenv;
import java.sql.*;
 
public class Main {
    public static void main(String[] args) throws Exception {
 
        // Lee automáticamente el archivo .env en la raíz del proyecto
        Dotenv dotenv = Dotenv.load();
 
        String apiKey = dotenv.get("EBIRD_API_KEY");
        String dbHost = dotenv.get("DB_HOST");
        String dbName = dotenv.get("DB_NAME");
        String dbUser = dotenv.get("DB_USER");
        String dbPass = dotenv.get("DB_PASSWORD");
 
        // Validar que la API key esté configurada
        if (apiKey == null || apiKey.isBlank()) {
            System.err.println("❌ ERROR: EBIRD_API_KEY no encontrada en el archivo .env");
            System.exit(1);
        }
 
        String dbUrl = "jdbc:mysql://" + dbHost + ":3306/" + dbName
            + "?useSSL=false&serverTimezone=America/Mexico_City&allowPublicKeyRetrieval=true";
 
        System.out.println("🔌 Conectando a MySQL en " + dbHost + "...");
 
        try (Connection conn = DriverManager.getConnection(dbUrl, dbUser, dbPass)) {
            System.out.println("✅ Conexión exitosa a la base de datos.");
 
            EBirdAPIClient         api = new EBirdAPIClient(apiKey);
            ETLService             etl = new ETLService(conn);
            DataAccumulatorService acc = new DataAccumulatorService(api, etl);
 
            acc.acumularDatos();
 
            System.out.println("\n🎯 ETL completo. Siguiente paso: correr 01_kmeans.py");
        }
    }
}