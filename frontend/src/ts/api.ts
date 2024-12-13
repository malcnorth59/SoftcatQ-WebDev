interface ApiResponse {
    success: boolean;
    message: string;
    data?: any;
}

class MembershipAPI {
    private static API_ENDPOINT = process.env.API_ENDPOINT || 'https://api.ukpc-membership.com';

    static async submitMembershipApplication(formData: MembershipForm): Promise<ApiResponse> {
        try {
            const response = await fetch(`${this.API_ENDPOINT}/membership/apply`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify(formData)
            });

            const data = await response.json();
            
            if (!response.ok) {
                throw new Error(data.message || 'Failed to submit application');
            }

            return {
                success: true,
                message: 'Application submitted successfully',
                data
            };
        } catch (error) {
            return {
                success: false,
                message: error instanceof Error ? error.message : 'An unknown error occurred'
            };
        }
    }
}

// Form submission handler
document.addEventListener('DOMContentLoaded', () => {
    const form = document.getElementById('membershipForm') as HTMLFormElement;
    
    form.addEventListener('submit', async (e) => {
        e.preventDefault();

        const formData: MembershipForm = {
            fullName: (document.getElementById('fullName') as HTMLInputElement).value,
            email: (document.getElementById('email') as HTMLInputElement).value,
            telephone: (document.getElementById('telephone') as HTMLInputElement).value,
            postcode: (document.getElementById('postcode') as HTMLInputElement).value,
            membershipType: (document.getElementById('membershipType') as HTMLSelectElement).value,
            laaStatus: (document.getElementById('laaStatus') as HTMLInputElement).checked
        };

        const validation = FormValidator.validateForm(formData);
        
        if (!validation.valid) {
            alert(validation.errors.join('\n'));
            return;
        }

        const response = await MembershipAPI.submitMembershipApplication(formData);
        
        if (response.success) {
            alert('Application submitted successfully. Please check your email for payment instructions.');
            form.reset();
        } else {
            alert(`Failed to submit application: ${response.message}`);
        }
    });
});