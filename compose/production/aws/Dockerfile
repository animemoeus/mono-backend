FROM docker.io/amazon/aws-cli:2.32.23

# Clear entrypoint to allow custom commands
ENTRYPOINT []

# Copy maintenance scripts
COPY ./compose/production/aws/maintenance /usr/local/bin/maintenance
COPY ./compose/production/postgres/maintenance/_sourced /usr/local/bin/maintenance/_sourced

# Make scripts executable and flatten structure
RUN chmod +x /usr/local/bin/maintenance/* \
    && mv /usr/local/bin/maintenance/* /usr/local/bin/ \
    && rmdir /usr/local/bin/maintenance

CMD ["/bin/bash"]
