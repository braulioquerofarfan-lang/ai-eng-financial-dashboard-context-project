import { describe, expect, it } from "vitest";

import { getLoadErrorMessage } from "./error-utils";

describe("getLoadErrorMessage", () => {
  it("maps TypeError to a connection message without exposing its message", () => {
    const error = new TypeError("Failed to fetch");
    const message = getLoadErrorMessage(error);

    expect(message).toBe(
      "Error de conexión. Verifica tu red e intenta de nuevo.",
    );
    expect(message).not.toContain(error.message);
  });

  it("maps other Errors to a server message without exposing their message", () => {
    const error = new Error("HTTP 500");
    const message = getLoadErrorMessage(error);

    expect(message).toBe(
      "No se pudieron cargar los datos. El servidor respondió con un error.",
    );
    expect(message).not.toContain(error.message);
  });

  it.each(["x", null])(
    "maps non-Error value %s to a server message without exposing it",
    (error) => {
      const message = getLoadErrorMessage(error);

      expect(message).toBe(
        "No se pudieron cargar los datos. El servidor respondió con un error.",
      );
      expect(message).not.toContain(String(error));
    },
  );
});
