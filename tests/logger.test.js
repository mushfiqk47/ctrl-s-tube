import { jest } from '@jest/globals';
import { LoggerService } from '../chrome-extension/services/logger.service.js';

describe('LoggerService', () => {
    let logger;
    let consoleSpy;

    beforeEach(() => {
        logger = new LoggerService('Test');
        consoleSpy = jest.spyOn(console, 'log').mockImplementation();
    });

    afterEach(() => {
        consoleSpy.mockRestore();
    });

    test('should log info messages when enabled', () => {
        logger.info('test message');
        expect(consoleSpy).toHaveBeenCalledWith(expect.stringContaining('[Test] test message'));
    });

    test('should not log when disabled', () => {
        logger.enabled = false;
        logger.info('test message');
        expect(consoleSpy).not.toHaveBeenCalled();
    });
});
