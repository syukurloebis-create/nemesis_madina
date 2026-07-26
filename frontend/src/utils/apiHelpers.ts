/**
 * API Helpers - Untuk response handling
 */

// Unwrap Axios response
export const unwrap = <T>(response: any): T => {
  return response?.data ?? response;
};

// Check if response is AxiosResponse
export const isAxiosResponse = (response: any): boolean => {
  return response?.data !== undefined && typeof response.status === 'number';
};

// Get data from response
export const getData = <T>(response: any): T => {
  return isAxiosResponse(response) ? response.data : response;
};

// Safe map over response
export const mapResponse = <T, R>(
  response: any,
  fn: (item: T) => R
): R[] => {
  const data = getData<T[]>(response);
  return Array.isArray(data) ? data.map(fn) : [];
};

export default { unwrap, isAxiosResponse, getData, mapResponse };
