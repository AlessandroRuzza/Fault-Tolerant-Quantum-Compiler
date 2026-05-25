#include "gaussian.hpp"

#include <cmath>
#include <stdexcept>
#include <string>

namespace {
double compute_inv_two_sigma_sq(double sigma, const char* axis_name) {
	if (sigma <= 0.0) {
		throw std::invalid_argument(std::string(axis_name) + " must be > 0");
	}
	return 1.0 / (2.0 * sigma * sigma);
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
	  inverse(inverse),
	  exponent_cutoff(compute_exponent_cutoff(weight)) {
}

double Gaussian::gaussian_at(int x, int y) const {
	if (x < 0 || x >= size_x || y < 0 || y >= size_y) {
		return 0.0;
	}

	const double dx = static_cast<double>(x - mean_x);
	const double dy = static_cast<double>(y - mean_y);

	const double exponent = -(dx * dx) * invTwoSigmaXSq - (dy * dy) * invTwoSigmaYSq;
	if (exponent < exponent_cutoff) return inverse ? weight : 0.0;
	const double gaussianValue = std::exp(exponent) * weight;

	if (!inverse) {
		return gaussianValue;
	}

	// inverse: valle al centro, weight lontano dal centro
	const double invertedValue = weight - gaussianValue;
	return invertedValue > 0.0 ? invertedValue : 0.0;
}
