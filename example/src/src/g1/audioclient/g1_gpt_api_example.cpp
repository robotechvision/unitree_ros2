#include "rclcpp/rclcpp.hpp"
#include "unitree_api/msg/request.hpp"
#include "unitree_api/msg/response.hpp"
#include <chrono>
#include <mutex>
#include <optional>

using namespace std::chrono_literals;

class GptTopicClient : public rclcpp::Node
{
public:
    GptTopicClient()
    : Node("gpt_topic_client")
    {
        request_pub_ = this->create_publisher<unitree_api::msg::Request>("/api/gpt/request", 20);
        response_sub_ = this->create_subscription<unitree_api::msg::Response>("/api/gpt/response", 20,
            std::bind(&GptTopicClient::handle_response, this, std::placeholders::_1));
    }

    void send_request(const std::string &text)
    {
        std::unique_lock<std::mutex> lock(mtx_);
        unitree_api::msg::Request msg;

        auto now = std::chrono::system_clock::now();
        auto duration = now.time_since_epoch();
        int64_t now_int = std::chrono::duration_cast<std::chrono::microseconds>(duration).count();

        // Msg
        msg.header.identity.id = now_int;
        msg.header.identity.api_id = 1001;
        msg.header.lease.id = 0;
        msg.header.policy.priority = 1;
        msg.header.policy.noreply = false;
        msg.parameter = text;

        while (true) {
            request_pub_->publish(msg);

            if (cv_.wait_for(lock, 0.5s, [this]() { return last_response_.has_value(); })) {
                RCLCPP_INFO(this->get_logger(), "GPT response: %s", last_response_->data.c_str());
                last_response_.reset();
                break;
            }
            else {
                RCLCPP_WARN(this->get_logger(), "No GPT response received in time.");
            }
        }
    }

private:
    rclcpp::Publisher<unitree_api::msg::Request>::SharedPtr request_pub_;
    rclcpp::Subscription<unitree_api::msg::Response>::SharedPtr response_sub_;

    std::mutex mtx_;
    std::condition_variable cv_;
    std::optional<unitree_api::msg::Response> last_response_;

    void handle_response(const unitree_api::msg::Response::SharedPtr msg)
    {
        std::lock_guard<std::mutex> lock(mtx_);
        last_response_ = *msg;
        cv_.notify_all();
    }
};

int main(int argc, char **argv)
{
    rclcpp::init(argc, argv);
    auto node = std::make_shared<GptTopicClient>();

    rclcpp::executors::SingleThreadedExecutor executor;
    executor.add_node(node);

    std::thread spin_thread([&executor]() { executor.spin(); });
    node->send_request("sing old mcdonald had a farm");
    // executor.spin();

    rclcpp::shutdown();
    return 0;
}
