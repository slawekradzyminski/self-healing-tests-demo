import { expect, test } from '../../fixtures/pages.fixture';
import { SEEDED_SANDBOX_USER } from '../../config/constants';
import { LoginClient } from '../../http-clients/LoginClient';
import { LlmToolsPage } from '../../pages/LlmToolsPage';

const IPHONE_CATALOG_PROMPT = 'Which iPhone models are currently available? Include their product details.';

test.describe('Catalog-grounded assistant smoke tests', () => {
  test('should answer an iPhone question through the catalog tools', async ({ page, request }) => {
    // given
    const loginClient = new LoginClient(request);
    const authenticatedUser = await loginClient.loginSuccessfully(SEEDED_SANDBOX_USER);
    await page.addInitScript(({ token, refreshToken }) => {
      window.localStorage.setItem('token', token);
      window.localStorage.setItem('refreshToken', refreshToken);
    }, {
      token: authenticatedUser.token,
      refreshToken: authenticatedUser.refreshToken
    });
    const toolsPage = new LlmToolsPage(page);
    await toolsPage.goto();
    await toolsPage.verifyLoaded();

    // when
    await toolsPage.sendMessage(IPHONE_CATALOG_PROMPT);

    // then
    await toolsPage.verifyCatalogLookupCompleted();
    await expect(toolsPage.assistantMessageContents.last()).not.toContainText('only these chat tool prompts are supported');
  });
});
