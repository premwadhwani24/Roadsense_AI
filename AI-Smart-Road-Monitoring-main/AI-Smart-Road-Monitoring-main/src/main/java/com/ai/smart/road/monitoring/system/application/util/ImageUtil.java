package com.ai.smart.road.monitoring.system.application.util;

import java.awt.image.BufferedImage;
import java.io.File;
import java.io.IOException;

import javax.imageio.ImageIO;

public class ImageUtil {

	public static BufferedImage readImage(String path) {
		try {
			return ImageIO.read(new File(path));
		} catch (IOException e) {
			throw new RuntimeException("Failed to read image: " + path, e);
		}
	}

	public static void saveImage(BufferedImage image, String format, String path) {
		try {
			ImageIO.write(image, format, new File(path));
		} catch (IOException e) {
			throw new RuntimeException("Failed to save image: " + path, e);
		}
	}

	public static boolean isValidImageFormat(String format) {
		String[] validFormats = ImageIO.getWriterFormatNames();
		for (String f : validFormats) {
			if (f.equalsIgnoreCase(format))
				return true;
		}
		return false;
	}
}
