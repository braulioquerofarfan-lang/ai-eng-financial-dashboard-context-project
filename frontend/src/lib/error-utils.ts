const CONNECTION_ERROR_MESSAGE =
  "Error de conexión. Verifica tu red e intenta de nuevo.";
const SERVER_ERROR_MESSAGE =
  "No se pudieron cargar los datos. El servidor respondió con un error.";

export function getLoadErrorMessage(error: unknown): string {
  return error instanceof TypeError
    ? CONNECTION_ERROR_MESSAGE
    : SERVER_ERROR_MESSAGE;
}
