package mx.zmg;

import com.fasterxml.jackson.databind.*;
import java.net.URI;
import java.net.http.*;
import java.time.LocalDate;
import java.util.*;

public class EBirdAPIClient {

    private static final String BASE_URL = "https://api.ebird.org/v2";
    private static final String API_KEY  = System.getenv("EBIRD_API_KEY");
    private final HttpClient httpClient  = HttpClient.newHttpClient();
    private final ObjectMapper mapper    = new ObjectMapper();

    public List<Avistamiento> fetchRecientes(int diasAtras) throws Exception {
        String url = BASE_URL + "/data/obs/MX-JAL/recent"
                   + "?back=" + diasAtras
                   + "&maxResults=10000&includeProvisional=true";
        return fetchAndParse(url);
    }

    public List<Avistamiento> fetchHistorico(LocalDate fecha) throws Exception {
        String url = String.format(
            "%s/data/obs/MX-JAL/historic/%d/%d/%d?maxResults=10000",
            BASE_URL, fecha.getYear(), fecha.getMonthValue(), fecha.getDayOfMonth()
        );
        return fetchAndParse(url);
    }

    public List<Avistamiento> fetchPorRadio(double lat, double lon, int radioKm) throws Exception {
        String url = String.format(
            "%s/data/obs/geo/recent?lat=%.4f&lng=%.4f&dist=%d&back=30&maxResults=10000",
            BASE_URL, lat, lon, radioKm
        );
        return fetchAndParse(url);
    }

    private List<Avistamiento> fetchAndParse(String url) throws Exception {
        if (API_KEY == null || API_KEY.isBlank()) {
            throw new RuntimeException("❌ Variable EBIRD_API_KEY no configurada.");
        }

        HttpRequest request = HttpRequest.newBuilder()
            .uri(URI.create(url))
            .header("x-ebirdapitoken", API_KEY)
            .header("Accept", "application/json")
            .GET()
            .build();

        HttpResponse<String> response = httpClient.send(
            request, HttpResponse.BodyHandlers.ofString()
        );

        if (response.statusCode() != 200) {
            throw new RuntimeException("eBird API error " + response.statusCode()
                                      + ": " + response.body());
        }
        return parseJSON(response.body());
    }

    private List<Avistamiento> parseJSON(String json) throws Exception {
        List<Avistamiento> resultado = new ArrayList<>();
        JsonNode array = mapper.readTree(json);

        for (JsonNode nodo : array) {
            try {
                String especie  = nodo.get("sciName").asText();
                double lat      = nodo.get("lat").asDouble();
                double lon      = nodo.get("lng").asDouble();
                String fechaStr = nodo.get("obsDt").asText().substring(0, 10);
                int cantidad    = nodo.has("howMany") && !nodo.get("howMany").isNull()
                                  ? nodo.get("howMany").asInt() : 1;

                Avistamiento a = new Avistamiento(especie, lat, lon,
                                                  LocalDate.parse(fechaStr), cantidad);
                if (a.isValido()) resultado.add(a);

            } catch (Exception ignored) {}
        }
        return resultado;
    }
}