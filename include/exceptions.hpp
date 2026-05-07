#ifndef EXCEPTIONS_HPP
#define EXCEPTIONS_HPP

#include <stdexcept>
#include <string>

class SafePassageException : public std::runtime_error {
public:
    explicit SafePassageException(const std::string& message)
        : std::runtime_error(message) {}
};

#endif // EXCEPTIONS_HPP