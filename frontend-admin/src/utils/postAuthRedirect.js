/**
 * After login/register, honor `location.state.from` when it is an in-app path.
 */
export function postAuthPath(isAdmin, fromState) {
  if (typeof fromState === "string" && fromState.startsWith("/")) {
    return fromState;
  }
  return isAdmin ? "/admin" : "/user";
}
