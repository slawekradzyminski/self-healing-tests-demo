import { expect, test } from '../../fixtures/pages.fixture';

test.describe('Public authentication smoke tests', () => {
  test('should render the login screen', async ({ loginPage }) => {
    // given
    // when
    await loginPage.goto();

    // then
    await loginPage.verifyLoaded();
  });

  test('should validate an empty password without leaving login', async ({ page, loginPage }) => {
    // given
    await loginPage.goto();

    // when
    await loginPage.login({ username: 'demo-user', password: '' });

    // then
    await expect(page).toHaveURL(loginPage.url);
    await expect(loginPage.passwordError).toHaveText('Password is required');
  });

  test('should open registration from login', async ({ page, loginPage, registerPage }) => {
    // given
    await loginPage.goto();

    // when
    await loginPage.clickRegisterButton();

    // then
    await expect(page).toHaveURL(registerPage.url);
    await expect(registerPage.registerPage).toBeVisible();
    await expect(registerPage.title).toHaveText('Create your account');
  });

  test('should validate an empty registration form', async ({ page, registerPage }) => {
    // given
    await registerPage.goto();

    // when
    await registerPage.submit();

    // then
    await expect(page).toHaveURL(registerPage.url);
    await registerPage.verifyRequiredFieldErrors();
    await registerPage.verifyNoToast();
  });
});
