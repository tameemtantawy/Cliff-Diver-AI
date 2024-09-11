import pygame

def rotate_shift_and_save_image(original_path, new_path, angle, shift_left, shift_up):
    # Initialize Pygame
    pygame.init()
    
    # Set up a minimal display
    pygame.display.set_mode((1, 1))  # Minimal non-intrusive display

    # Load the original image
    image = pygame.image.load(original_path).convert_alpha()

    # Rotate the image
    rotated_image = pygame.transform.rotate(image, angle)
    
    # Create a new surface to hold the shifted image
    # This surface has the same size as the rotated image
    shifted_surface = pygame.Surface(rotated_image.get_size(), pygame.SRCALPHA)

    # Blit the rotated image onto the new surface, shifted to the left and up
    shifted_surface.blit(rotated_image, (-shift_left, -shift_up))  # Shift left and up

    # Save the new rotated and shifted image
    pygame.image.save(shifted_surface, new_path)

    # Quit Pygame
    pygame.quit()

# Define paths, rotation angles, and shift values
original_images = {
    'Entry2.png': (-2, 0, 0),  # Rotate by 0 degrees, shift left by 50 pixels, shift up by 10 pixels
}

# Process each image
for path, (angle, shift_left, shift_up) in original_images.items():
    new_path = path  # This will prefix the filename with 'shifted_'
    rotate_shift_and_save_image(path, new_path, angle, shift_left, shift_up)
