#include "gaussian.hpp"

#include <iostream>

#include <cmath>
#include <limits>
#include <stdexcept>
#include <string>

namespace {
double compute_inv_two_sigma_sq(double sigma, const char* axis_name) {
	if (sigma <= 0.0) {
		throw std::invalid_argument(std::string(axis_name) + " must be > 0");
	}
	return 1.0 / (2.0 * sigma * sigma);
}

double compute_axis_sum(int mean, int size, double inv_two_sigma_sq) {
	double sum = 0.0;
	for (int x = 0; x < size; ++x) {
		const double d = static_cast<double>(x - mean);
		sum += std::exp(-(d * d) * inv_two_sigma_sq);
	}
	return sum;
}

double compute_norm_factor(int mean_x, int mean_y, int size_x, int size_y, double inv_two_sigma_x_sq, double inv_two_sigma_y_sq) {
	if (size_x <= 0 || size_y <= 0) {
		throw std::invalid_argument("size_x and size_y must be > 0");
	}

	const double sum_x = compute_axis_sum(mean_x, size_x, inv_two_sigma_x_sq);
	const double sum_y = compute_axis_sum(mean_y, size_y, inv_two_sigma_y_sq);
	const double product = sum_x * sum_y;

	if (product <= std::numeric_limits<double>::min()) {
		throw std::runtime_error("Gaussian normalization failed");
	}

	return (1.0 / product);
}
} // namespace

Gaussian::Gaussian(int mean_x, int mean_y, double sigma_x, double sigma_y, int size_x, int size_y, double weight, bool inverse)
	: mean_x(mean_x),
	  mean_y(mean_y),
	  sigmaX(sigma_x),
	  sigmaY(sigma_y),
	  size_x(size_x),
	  size_y(size_y),
	  weight(weight),
	  invTwoSigmaXSq(compute_inv_two_sigma_sq(sigmaX, "sigma_x")),
	  invTwoSigmaYSq(compute_inv_two_sigma_sq(sigmaY, "sigma_y")),
	  normFactor(compute_norm_factor(mean_x, mean_y, size_x, size_y, invTwoSigmaXSq, invTwoSigmaYSq)),
	  inverse(inverse) {
}

double Gaussian::gaussian_at(int x, int y) const {
	if (x < 0 || x >= size_x || y < 0 || y >= size_y) {
		return 0.0;
	}

	const double dx = static_cast<double>(x - mean_x);
	const double dy = static_cast<double>(y - mean_y);

	const double exponent = -(dx * dx) * invTwoSigmaXSq - (dy * dy) * invTwoSigmaYSq;
	const double gaussianValue = std::exp(exponent) * normFactor * weight;

	if (!inverse) {
		return gaussianValue;
	}

	// Mirror the gaussian around its peak so inverse=true is a true "valley":
	// minimum at the mean and higher values away from the center.
	const double peakValue = normFactor * weight;
	const double invertedValue = peakValue - gaussianValue;
	return invertedValue > 0.0 ? invertedValue : 0.0;
}
