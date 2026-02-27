# used by ./generate-files.sh

FROM ruby:3.4.3
RUN apt-get update -qq && apt-get install -y build-essential
RUN mkdir /app
WORKDIR /app
COPY Gemfile /app/Gemfile
COPY Gemfile.lock /app/Gemfile.lock
RUN bundle install
VOLUME /app
ENTRYPOINT ["bundle", "exec", "rake"]
