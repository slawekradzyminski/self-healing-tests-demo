import { expect, type Locator, type Page } from '@playwright/test';
import { LlmModePage } from './LlmModePage';

export class LlmToolsPage extends LlmModePage {
  readonly toolsPage: Locator;
  readonly settingsPanel: Locator;
  readonly toolDefinitionJson: Locator;
  readonly systemPrompt: Locator;
  readonly systemPromptContent: Locator;
  readonly chatInput: Locator;
  readonly sendButton: Locator;
  readonly toolCallNotices: Locator;
  readonly toolMessages: Locator;
  readonly assistantMessageContents: Locator;

  constructor(page: Page) {
    super(page, '/llm/tools', 'llm-tools-mode', 'Catalog-grounded assistant');
    this.toolsPage = this.byTestId('ollama-tool-chat-page');
    this.settingsPanel = this.byTestId('tool-settings-panel');
    this.toolDefinitionJson = this.byTestId('tool-definition-json');
    this.systemPrompt = this.byTestId('tool-system-prompt');
    this.systemPromptContent = this.byTestId('tool-system-prompt-content');
    this.chatInput = this.byTestId('chat-input');
    this.sendButton = this.byTestId('chat-send-button');
    this.toolCallNotices = this.byTestId('tool-call-notice');
    this.toolMessages = this.byTestId('tool-message');
    this.assistantMessageContents = this.byTestId('chat-message-content-assistant');
  }

  override async verifyLoaded() {
    await super.verifyLoaded();
    await expect(this.toolsPage).toBeVisible();
    await expect(this.settingsPanel).toBeVisible();
    await expect(this.toolDefinitionJson).toBeVisible();
    await expect(this.systemPrompt).toBeVisible();
    await expect(this.chatInput).toBeVisible();
    await expect(this.sendButton).toBeDisabled();
  }

  async verifyToolDefinitions() {
    await expect(this.toolDefinitionJson).toContainText('get_product_snapshot');
    await expect(this.toolDefinitionJson).toContainText('list_products');
  }

  async verifySystemPrompt() {
    await expect(this.systemPromptContent).toContainText('tool-calling shopping assistant');
    await expect(this.systemPromptContent).toContainText('list_products');
    await expect(this.systemPromptContent).toContainText('get_product_snapshot');
  }

  async typeMessage(message: string) {
    await this.chatInput.fill(message);
  }

  async verifyReadyToSend(message: string) {
    await expect(this.chatInput).toHaveValue(message);
    await expect(this.sendButton).toBeEnabled();
  }

  async sendMessage(message: string) {
    await this.chatInput.fill(message);
    await this.sendButton.click();
  }

  async verifyCatalogLookupCompleted() {
    await expect(this.toolCallNotices).toHaveCount(2, { timeout: 60_000 });
    await expect(this.toolCallNotices).toContainText(['list_products', 'get_product_snapshot']);
    await expect(this.toolMessages).toHaveCount(2);
    await expect(this.toolMessages).toContainText(['list_products', 'get_product_snapshot']);
    await expect(this.assistantMessageContents.last()).toContainText('iPhone 13 Pro');
    await expect(this.chatInput).toBeEnabled();
  }
}
