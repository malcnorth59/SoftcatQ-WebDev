interface MembershipForm {
    fullName: string;
    email: string;
    telephone: string;
    postcode: string;
    membershipType: string;
    laaStatus: boolean;
}

class FormValidator {
    static validateFullName(name: string): boolean {
        return name.length >= 2;
    }

    static validateEmail(email: string): boolean {
        const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
        return emailRegex.test(email);
    }

    static validateTelephone(telephone: string): boolean {
        const phoneRegex = /^[\d\s\-+()]{10,}$/;
        return phoneRegex.test(telephone);
    }

    static validatePostcode(postcode: string): boolean {
        const ukPostcodeRegex = /^[A-Z]{1,2}[0-9][A-Z0-9]? ?[0-9][A-Z]{2}$/i;
        return ukPostcodeRegex.test(postcode);
    }

    static validateForm(formData: MembershipForm): { valid: boolean; errors: string[] } {
        const errors: string[] = [];

        if (!this.validateFullName(formData.fullName)) {
            errors.push("Please enter a valid full name");
        }

        if (!this.validateEmail(formData.email)) {
            errors.push("Please enter a valid email address");
        }

        if (!this.validateTelephone(formData.telephone)) {
            errors.push("Please enter a valid telephone number");
        }

        if (!this.validatePostcode(formData.postcode)) {
            errors.push("Please enter a valid UK postcode");
        }

        if (!formData.membershipType) {
            errors.push("Please select a membership type");
        }

        return {
            valid: errors.length === 0,
            errors
        };
    }
}