package mx.zmg;

import java.sql.*;
import java.util.List;

public class ETLService {

    private static final int BATCH_SIZE = 500;
    private final Connection connection;

    public ETLService(Connection connection) {
        this.connection = connection;
    }

    public void cargar(List<Avistamiento> avistamientos) throws SQLException {
        String sql = """
            INSERT INTO RegistrosDeAvistamiento
            (nombre_cientifico, latitud, longitud, fecha, cantidad)
            VALUES (?, ?, ?, ?, ?)
            ON DUPLICATE KEY UPDATE cantidad = VALUES(cantidad)
            """;

        connection.setAutoCommit(false);

        try (PreparedStatement ps = connection.prepareStatement(sql)) {
            int contador = 0;
            for (Avistamiento a : avistamientos) {
                ps.setString(1, a.getNombreCientifico());
                ps.setDouble(2, a.getLatitud());
                ps.setDouble(3, a.getLongitud());
                ps.setDate(4, java.sql.Date.valueOf(a.getFecha()));
                ps.setInt(5, a.getCantidad());
                ps.addBatch();

                if (++contador % BATCH_SIZE == 0) {
                    ps.executeBatch();
                    System.out.printf("[CARGAR] Insertados: %d%n", contador);
                }
            }
            ps.executeBatch();
            connection.commit();
            System.out.printf("[CARGAR] ✅ Total insertado: %d registros%n", contador);

        } catch (SQLException e) {
            connection.rollback();
            throw e;
        } finally {
            connection.setAutoCommit(true);
        }
    }
}