#ifndef GAUSSIAN_HPP
#define GAUSSIAN_HPP

class Gaussian {
public:
    Gaussian(int mean_x, int mean_y, double sigma_x, double sigma_y, int size_x, int size_y, double weight, bool inverse);

    double gaussian_at(int x, int y) const;

    inline void update_weight(double new_weight) { weight = new_weight; }

    inline void update_inverse(bool new_inverse) { inverse = new_inverse; }
    
private:
    const int mean_x;
    const int mean_y;
    const double sigmaX;
    const double sigmaY;
    const int size_x;
    const int size_y;
    const double invTwoSigmaXSq;
    const double invTwoSigmaYSq;
    const double normFactor;
    bool inverse;
    double weight;
};



#endif // GAUSSIAN_HPP
