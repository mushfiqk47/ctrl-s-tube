import { isValidYouTubeUrl, isValidUUID, sanitizeFilename, extractVideoId } from '../chrome-extension/utils/validation.js';

describe('Validation Utils', () => {
    describe('isValidYouTubeUrl', () => {
        test('should return true for valid YouTube URLs', () => {
            expect(isValidYouTubeUrl('https://www.youtube.com/watch?v=dQw4w9WgXcQ')).toBe(true);
            expect(isValidYouTubeUrl('https://youtu.be/dQw4w9WgXcQ')).toBe(true);
        });

        test('should return false for invalid URLs', () => {
            expect(isValidYouTubeUrl('https://google.com')).toBe(false);
            expect(isValidYouTubeUrl('not a url')).toBe(false);
        });
    });

    describe('extractVideoId', () => {
        test('should extract ID from standard URL', () => {
            expect(extractVideoId('https://www.youtube.com/watch?v=dQw4w9WgXcQ')).toBe('dQw4w9WgXcQ');
        });

        test('should extract ID from short URL', () => {
            expect(extractVideoId('https://youtu.be/dQw4w9WgXcQ')).toBe('dQw4w9WgXcQ');
        });

        test('should return null for invalid URLs', () => {
            expect(extractVideoId('https://google.com')).toBeNull();
        });
    });

    describe('isValidUUID', () => {
        test('should return true for valid UUID v4', () => {
            expect(isValidUUID('123e4567-e89b-12d3-a456-426614174000')).toBe(true);
        });

        test('should return false for invalid UUID', () => {
            expect(isValidUUID('invalid-uuid')).toBe(false);
        });
    });

    describe('sanitizeFilename', () => {
        test('should remove invalid characters', () => {
            expect(sanitizeFilename('file/name:with?invalid*chars')).toBe('filenamewithinvalidchars');
        });

        test('should replace spaces with underscores', () => {
            expect(sanitizeFilename('file name with spaces')).toBe('file_name_with_spaces');
        });

        test('should truncate long filenames', () => {
            const longName = 'a'.repeat(150);
            expect(sanitizeFilename(longName, 10).length).toBe(10);
        });
    });
});
