package mx.zmg;

import java.time.LocalDate;

public class Avistamiento {
    private String nombreCientifico;
    private double latitud;
    private double longitud;
    private LocalDate fecha;
    private int cantidad;

    public Avistamiento(String nombreCientifico, double latitud,
                        double longitud, LocalDate fecha, int cantidad) {
        this.nombreCientifico = nombreCientifico;
        this.latitud = latitud;
        this.longitud = longitud;
        this.fecha = fecha;
        this.cantidad = cantidad;
    }

    // Bounding box de la ZMG
    public boolean isValido() {
        return latitud  >= 20.3  && latitud  <= 21.0 &&
               longitud >= -103.6 && longitud <= -102.9 &&
               cantidad > 0 &&
               nombreCientifico != null && !nombreCientifico.isBlank();
    }

    public String getNombreCientifico() { return nombreCientifico; }
    public double getLatitud()          { return latitud; }
    public double getLongitud()         { return longitud; }
    public LocalDate getFecha()         { return fecha; }
    public int getCantidad()            { return cantidad; }

    @Override
    public String toString() {
        return String.format("[%s] lat=%.4f lon=%.4f fecha=%s cant=%d",
                             nombreCientifico, latitud, longitud, fecha, cantidad);
    }
}