import authService from '../../../auth';

const TEST_API_URL =
  process.env.NEMESIS_TEST_API_URL ||
  'http://127.0.0.1:8000/api';

const TEST_USERNAME =
  process.env.NEMESIS_TEST_USERNAME;

const TEST_PASSWORD =
  process.env.NEMESIS_TEST_PASSWORD;

export async function loginForTests(): Promise<void> {
  if (!TEST_USERNAME || !TEST_PASSWORD) {
    throw new Error(
      'Missing NEMESIS_TEST_USERNAME or NEMESIS_TEST_PASSWORD environment variables.'
    );
  }

  const response = await fetch(
    `${TEST_API_URL}/v1/auth/login`,
    {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        username: TEST_USERNAME,
        password: TEST_PASSWORD,
      }),
    },
  );

  if (!response.ok) {
    const body = await response.text();

    throw new Error(
      `Test login failed: HTTP ${response.status} ${body}`,
    );
  }

  const data = await response.json();

  if (!data.access_token) {
    throw new Error(
      'Test login succeeded but access_token is missing.',
    );
  }

  authService.setTokens(
    data.access_token,
    data.refresh_token || '',
  );
}
