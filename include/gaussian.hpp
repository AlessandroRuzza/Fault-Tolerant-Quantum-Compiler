#ifndef GAUSSIAN_HPP
#define GAUSSIAN_HPP

class Gaussian {
public:
    Gaussian(int mean_x, int mean_y, double sigma_x, double sigma_y, int size_x, int size_y, double weight, bool inverse);

    double gaussian_at(int x, int y) const;

    inline void update_weight(double new_weight) { weight = new_weight; }

    inline void update_inverse(bool new_inverse) { inverse = new_inverse; }

    inline int get_mean_x() const { return mean_x; }
    inline int get_mean_y() const { return mean_y; }
    inline double get_sigma_x() const { return sigmaX; }
    inline double get_sigma_y() const { return sigmaY; }
    inline int get_size_x() const { return size_x; }
    inline int get_size_y() const { return size_y; }
    inline double get_weight() const { return weight; }
    inline bool is_inverse() const { return inverse; }
    inline double get_peak_value() const { return weight; }

private:
    const int mean_x;
    const int mean_y;
    const double sigmaX;
    const double sigmaY;
    const int size_x;
    const int size_y;
    const double invTwoSigmaXSq;
    const double invTwoSigmaYSq;
    bool inverse;
    double weight;
};



#endif // GAUSSIAN_HPP
