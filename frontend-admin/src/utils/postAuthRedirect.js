/**
 * After login/register, honor `location.state.from` when it is an in-app path.
 * Rejects scheme-relative URLs (`//...`).
 */
export function postAuthPath(isAdmin, fromState) {
  if (
    typeof fromState === "string" &&
    fromState.startsWith("/") &&
    !fromState.startsWith("//")
  ) {
    return fromState;
  }
  return isAdmin ? "/admin" : "/user";
}
